# Carnegie Mellon SAMS Alexa course - Flash Quiz Project
# adapted from:
# https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/flask-ask-a-new-python-framework-for-rapid-alexa-skills-kit-development
# [20170711} (air) Initial version
#
# Student(s): David Garcia, Jenna McClellan, Jazmine Freund, Natalie Cardenas
#
# <comment on your features>
#
#
from flask import Flask#, render_template
from flask_ask import Ask, statement, question, session
from QuizletAPI import *
from fuzzywuzzy import fuzz
from random import randint

app = Flask(__name__)
ask = Ask(app, "/")
# logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# helper functions
def get_question(prefix=False, format = ""):
    msg = {
        0: "If you want to find a specific set, say Specific... otherwise, say Browse", #"Please say... specific... to search for a specific set, or... browse... to search among all sets on Quizlet"
        1: "What type of quiz are you looking to study off of? ",
        2: ("You want to look for a... {}... quiz, is that correct? ").format(format),
        3: "What size study set do you want? Small, Medium or Large. ",
        4: "What is the username of the owner of the set? ",
        5: ("The username is... {}... is that correct? ").format(format),
        6: "What is the name of the set you are looking for? ",
        "Default": ""
    }[session.attributes["state"] if session.attributes["state"] < 7 and almostEqual(session.attributes["state"]%1 , 0) else "Default"]

    if session.attributes["state"] == 7:
        if( session.attributes["errorCode"] == "" ):
            msg = "I've selected the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that alright?"
        if(session.attributes["errorCode"] != ""):
            session.attributes["state"] = 0
            msg = session.attributes["errorCode"] + " We will now restart the quiz finding process... " + get_question()
            session.attributes["errorCode"] = ""

    elif session.attributes["state"] == 8:
        msg = "Define the following term. " if(session.attributes["termFirst"]) else "What term best fits the following definition? "
        msg += session.attributes["unFamiliar"][0]["term" if(session.attributes["termFirst"]) else "definition"]
    elif session.attributes["state"] == 9:
        msg = "You have finished all of the questions for this set. Would you like to quit, retry, or choose a new quiz"
    elif almostEqual(session.attributes["state"]%1 , .8):
        msg = "Are you sure you want to restart your quiz?"
    elif  almostEqual(session.attributes["state"]%1 , .9):
        msg = "Are you sure you want to search for a new quiz?"
    print( str(session.attributes["state"]) + ": " + msg )
    return ("Sorry, I didn't catch that... " + msg) if(prefix) else msg

def get_quiz_info(get):
    quizletObject = Quizlet("pzts2bDXSN")
    if(session.attributes["quizInformation"]["category"] != "" and session.attributes["quizInformation"]["length"] != ""):
        setArray = quizletObject.search_sets(session.attributes["quizInformation"]["category"], paged=False)
        if(len(setArray["sets"]) == 0):
            session.attributes["errorCode"] = "There are no results matching your search: " + session.attributes["quizInformation"]["category"] + ". "
            print("Error encountered: " + session.attributes["errorCode"])
            return ""
        firstSet = setArray["sets"][session.attributes["quizTryCount"]]
        while not isValidQuiz(firstSet):
            session.attributes["quizTryCount"]+= 1

            if(session.attributes["quizTryCount"] < len(setArray["sets"])):
                firstSet = setArray["sets"][session.attributes["quizTryCount"]]
            else:
                session.attributes["quizTryCount"] = 0
                session.attributes["pageTryCount"] += 1
                setArray = quizletObject.make_request('search/sets', {'q': session.attributes["quizInformation"]["category"], 'page': session.attributes["pageTryCount"]})
                if(len(setArray) == 0):
                    session.attributes["errorCode"] = "There are no results matching your search: " + session.attributes["quizInformation"]["category"] + ". "
                    return ""
        print("Quiz #" + str(session.attributes["quizTryCount"]) + " selected")
    elif(session.attributes["quizInformation"]["username"] != "" and session.attributes["quizInformation"]["title"] != ""):

        universal = quizletObject.make_paged_request('search/universal', {'q': session.attributes["quizInformation"]["username"]})
        users = []
        try:
            for current in universal['items']:
                if current["type"] == "user":
                    users.append(current["username"])
        except TypeError:
            for item in universal[0]["items"]:
                if item["type"] == "user":
                    users.append(item["username"])
        if(len(users) == 0):
            session.attributes["errorCode"] = "The user " + session.attributes["quizInformation"]["username"] + " does not exist."
            print("Error encountered: " + session.attributes["errorCode"])
            return ""
        max = 0
        for x in range(1, len(users)):
            if fuzz.token_set_ratio(users[x], session.attributes["quizInformation"]["username"]) > fuzz.token_set_ratio(users[max], session.attributes["quizInformation"]["username"]):
                max = x
        username = users[max]
        if( len(quizletObject.make_paged_request('users/' + username + '/sets')) > 0):
            setArray = quizletObject.make_paged_request('users/' + username + '/sets')[0]
        else:
            session.attributes["errorCode"] = "The user " + session.attributes["quizInformation"]["username"] + " has no sets available."
            print("Error encountered: " + session.attributes["errorCode"])
            return ""
        print("User " + session.attributes["quizInformation"]["username"] + " selected")

        for z in range(0, session.attributes["quizTryCount"]+1):
            max = 0
            if(len(setArray) == 0):
                session.attributes["errorCode"] = "There are no sets matching " + session.attributes["quizInformation"]["title"] + " by " + session.attributes["quizInformation"]["username"] + ". "
                print("Error encountered: " + session.attributes["errorCode"])
                return ""
            for x in range(1, len(setArray)):
                if fuzz.token_set_ratio(setArray[x]["title"], session.attributes["quizInformation"]["title"]) > fuzz.token_set_ratio(setArray[max]["title"], session.attributes["quizInformation"]["title"]):
                    max = x
            firstSet = setArray[max]
            setArray.pop(max)
        print("Set " + firstSet["title"] + " selected")
    else: return question(get_question(prefix=True))
    set = quizletObject.get_set( firstSet["id"] ) #305754982
    return set[get]

def isValidQuiz(quiz):
    if(
    (quiz["has_images"]) or
    (quiz["visibility"] != "public") or
    (not quiz["has_access"]) or
    (quiz["lang_terms"] != "en") or
    (quiz["lang_definitions"] != "en") ):
        return False

    if( (session.attributes["quizInformation"]["length"] == "any") or
    (session.attributes["quizInformation"]["length"] == "small" and quiz["term_count"] <= 9) or
    (session.attributes["quizInformation"]["length"] == "medium"  and 9 < quiz["term_count"] <= 14) or
    (session.attributes["quizInformation"]["length"] == "large"  and 14 < quiz["term_count"]) ):
        return True
    return False

def shuffle_cards(mixInOld=True):
    if( session.attributes["errorCode"] != "" ):
        session.attributes["errorCode"] = ""
        session.attributes["state"] = 0
        return question("There are no results matching your search: " + session.attributes["quizInformation"]["category"] +". "+ get_question())
    if( len(session.attributes["unFamiliar"]) == 0 ):
        session.attributes["unFamiliar"] = get_quiz_info("terms")
    elif(mixInOld):
        session.attributes["unFamiliar"].extend(session.attributes["familiar"])
        session.attributes["familiar"] = []
    temp = []
    while len(session.attributes["unFamiliar"]) > 0:
        temp.append( session.attributes["unFamiliar"].pop(0) )
    while( len(temp) > 0):
        session.attributes["unFamiliar"].append( temp.pop( randint(0, len(temp)-1) ) )
    print("Flashcards: ")
    for cards in session.attributes["unFamiliar"]:
        print(cards["term"] + ": " + cards["definition"])

def almostEqual(d1, d2):
    epsilon = 10**(-5)
    return (abs(d2 - d1) < epsilon)

def instantiateQuiz(newQuiz = True):
    if(newQuiz):
        #default values:
        session.attributes["quizInformation"] = dict()
        session.attributes["quizInformation"]["QuizPath"] = "" #browse or specific
        session.attributes["quizInformation"]["category"] = "" #Browse - which category a user wants to browse
        session.attributes["quizInformation"]["length"] = "" #Browse - small, medium, or large
        session.attributes["quizInformation"]["username"] = "" #Specific - the username of the owner of a set
        session.attributes["quizInformation"]["title"] = "" #Specific - the name of the specific set
        session.attributes["unFamiliar"] = []
        session.attributes["familiar"] = []
        session.attributes["pageTryCount"] = 1
        session.attributes["errorCode"] = ""
    else: #restart current quiz
        shuffle_cards()
    session.attributes["quizTryCount"] = 0
    session.attributes["wrongAnswers"] = 0
    print("New quiz instantiated")

def abridgify(input):
    remove = ["the", "uh", "a", "an"]
    converted = ""
    for word in input.split(" "):
        if not(word in remove):
            converted+= word+" "
    return converted

@ask.launch
def WelcomeIntent():
    if "state" in session.attributes:
        prefix = ""
    else:
        session.attributes["state"] = 0
        prefix = "Welcome to Flash Quiz... "

    instantiateQuiz()
    msg = prefix + get_question()
    return question(msg)


@ask.intent("BrowseIntent") #Sample utterance: "browse"
def BrowseIntent():
    if(session.attributes["state"] == 0):
        session.attributes["state"] = 1
    return question( get_question() if(session.attributes["state"] == 1) else get_question(prefix=True) )

@ask.intent("SpecificIntent") #Sample utterance: "Specific"
def SpecificIntent():
    if(session.attributes["state"] == 0):
        session.attributes["state"] = 4
    return question( get_question() if(session.attributes["state"] == 4) else get_question(prefix=True) )


@ask.intent("YesIntent") #Sample utterance: "YES"
def YesIntent():
    #Important States: 2, 5, 7, n.8, n.9

    if (session.attributes["state"] == 2): #User confirms the quiz type
        session.attributes["state"] = 3
        msg = get_question()
    elif (session.attributes["state"] == 5): #User confirms the owner's name
        session.attributes["state"] = 6

        msg = get_question()
    elif (session.attributes["state"] == 7): #User confirms this is the right quiz set
        session.attributes["state"] = 8
        session.attributes["quizTryCount"] = 0
        shuffle_cards()
        session.attributes["termFirst"] = False
        prefix = "We will now begin the quiz... say Switch if you want to switch from terms to definitions... Restart to restart your quiz... and New Quiz to search for a new one... "
        msg = prefix + get_question()
    elif almostEqual(session.attributes["state"]%1 , .8): #restart quiz
        session.attributes["state"] = 8
        instantiateQuiz(newQuiz=False)
        msg = "Restarting set now! " + get_question()
    elif almostEqual(session.attributes["state"]%1 , .9): #find a new quiz
        session.attributes["state"] = 0
        instantiateQuiz()
        msg = get_question()
    else:
        msg = get_question(prefix=True)
    return question(msg)

@ask.intent("NoIntent") #Sample utterance: "NO"
def NoIntent():
    #Important States: 2, 5, 7, n.8, n.9

    if (session.attributes["state"] == 2): #Re-ask for quiz type
        session.attributes["state"] = 1
        session.attributes["quizInformation"]["category"] = ""
        msg = get_question()
    elif (session.attributes["state"] == 5): #Re-ask for the owner's name
        session.attributes["state"] = 4
        session.attributes["quizInformation"]["username"] = ""
        msg = get_question()
    elif (session.attributes["state"] == 7): #Not the right quiz
        session.attributes["quizTryCount"] += 1
        print(session.attributes["quizTryCount"])
        msg = get_question()
    elif almostEqual(session.attributes["state"]%1 , .8) or almostEqual(session.attributes["state"]%1 , .9): #User says no to finding a new quiz or restarting current quiz
        session.attributes["state"] //= 1
        msg = get_question()
    else:
        msg = get_question(prefix=True)
    return question(msg)


@ask.intent("SmallIntent") #Sample utterance: "Small, Tiny, Mini, Short"
def SmallIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "small"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("MediumIntent") #Sample utterance: "Medium, Moderate"
def MediumIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "medium"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("LargeIntent") #Sample utterance: "Large, Big"
def LargeIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "large"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("AnySizeIntent") #Sample utterance: "any, I don't care, however long, any size"
def AnySizeIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "any"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("SwitchCardIntent") #Sample utterance: "switch cards, term to definition, definition to term, term first, definition first"
def SwitchCardIntent():
    if (session.attributes["state"] == 8):
        session.attributes["termFirst"] = not session.attributes["termFirst"]
    return question( get_question() if(session.attributes["state"] == 8 or session.attributes["state"] == 9) else get_question(prefix=True) )


@ask.intent("AnswerIntent",  convert={'response': string})
def AnswerIntent(response):
    #Important States: 1,  4, 6,  8
    repeat = ["repeat the question", "what did you say", "wait what", "what was the question", "can you repeat that?"]
    for word in repeat:
        if(word.lower() in response.lower()):
            return get_question()
    #Path: Browse
    if (session.attributes["state"] == 1): #User answers with type of quiz
        session.attributes["state"] = 2
        session.attributes["quizInformation"]["category"] = response
        msg = get_question(format=response)

    #Path: Specific
    elif (session.attributes["state"] == 4): #User answers with the username of the set owner
        session.attributes["state"] = 5
        response = response.lower()
        for char in response:
            if not(char in "abcdefghijklmnopqrstuwxyz1234567890"):
                response = response.replace(char, "")
        response.replace("underscore", "_")
        response.replace("questionmark", "?")
        response.replace("exclamationpoint", "!")

        session.attributes["quizInformation"]["username"] = response
        msg = get_question(format=session.attributes["quizInformation"]["username"])
    elif (session.attributes["state"] == 6): #User answers with the name of the set
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["title"] = response.title()
        msg = get_question()

    #Path: Flashcards
    elif (session.attributes["state"] == 8):
        answer = session.attributes["unFamiliar"][0]["definition" if(session.attributes["termFirst"]) else "term"]

        idk = ["I don't know", "I'm not sure", "skip this"]
        for word in idk:
            if(word.lower() in response.lower()):
                session.attributes["wrongAnswers"] = 0
                session.attributes["unFamiliar"].append( session.attributes["unFamiliar"].pop(0) )
                return question("The answer we were looking for was " + answer + ". " + get_question())
        ratio = fuzz.token_set_ratio(abridgify(response), abridgify(answer)) #out of 100
        print("\n", abridgify(response), abridgify(answer), ratio)
        if(ratio>=85):
            session.attributes["familiar"].append(session.attributes["unFamiliar"].pop(0))
            prefix = "Good job, you got that one correct... "
        elif(ratio >= 65 and session.attributes["wrongAnswers"]%2 == 1):
            prefix = "You were close! Try rephrasing or altering your answer... "
        else:
            prefix = "That wasn't quite right! "

        if( ratio < 85): #the user answered wrong twice
            session.attributes["wrongAnswers"]+=1
            if(session.attributes["wrongAnswers"]%2 == 1):
                prefix += "Try again... "
            else:
                session.attributes["wrongAnswers"] = 0
                prefix += "The answer we were looking for was " + answer + ". " + " "
                session.attributes["unFamiliar"].append( session.attributes["unFamiliar"].pop(0) )
        else:
            session.attributes["wrongAnswers"] = 0

        if( len(session.attributes["unFamiliar"]) == 0 ):
            session.attributes["state"] = 9

        msg = prefix + get_question()

    else:
        msg = get_question(prefix=True)
    return question(msg)


@ask.intent("QuitIntent") #Sample utterance: "QUIT", "END", "STOP"
def QuitIntent():
    """
    msg = "Thank you for using Flash Quiz! Goodbye! "
    feedback = "Great job! " if len(session.attributes["familiar"]) > len(session.attributes["unFamiliar"]) else "Don't forget to keep studying! "
    msg = ("You saw {} terms and have mastered {} terms. "+ str(feedback) ).format(
		  len(session.attributes["familiar"]) + len(session.attributes["unFamiliar"]), len(session.attributes["familiar"]) )
    """
    return statement("Goodbye")

@ask.intent("RedoIntent") #Sample utterances: "REDO", "RETRY", "TRY AGAIN", "RESTART"
def RedoIntent():
    prefix = ""
    if (session.attributes["state"] == 9): #user wants to redo quiz after finishing current quiz
        session.attributes["state"] = 8
        instantiateQuiz(newQuiz=False)
        prefix = "Restarting set now! "
    elif(session.attributes["state"] == 8):
        session.attributes["state"] += .8
    return question(get_question() if 8 < session.attributes["state"] < 9 else get_question(prefix=True))

@ask.intent("NewQuizIntent") #Sample utterances: "NEW QUIZ", "NEW", "DIFFERENT QUIZ"
def NewQuizIntent():
    if(session.attributes["state"] == 9):
        session.attributes["state"] = 0
    elif(session.attributes["state"] > 0):
        session.attributes["state"] += .9
    msg = get_question() if (session.attributes["state"] == 0 or almostEqual(session.attributes["state"]%1 , .9)) else get_question(prefix=True)
    return question(msg)

@ask.intent("AMAZON.HelpIntent") #Sample utterances: "NEW QUIZ", "NEW", "DIFFERENT QUIZ"


##########################
if __name__ == "__main__":
    app.run(debug=True)
