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
def get_question(prefix=False, format = "", tryGetQuiz=0):
    msg = {
        0: "Do you want a specific set or to browse for a set? ", #"Please say... specific... to search for a specific set, or... browse... to search among all sets on Quizlet"
        1: "What type of quiz are you looking to study off of? ",
        2: ("You want to look for a... {}... quiz, is that correct? ").format(format),
        3: "What size study set do you want? Small, Medium or Large. ",
        4: "What is the username of the owner of the set? ",
        5: ("The username is... {}... is that correct? ").format(format),
        6: "What is the name of the set you are looking for? ",
        "Default": ""
    }[session.attributes["state"] if session.attributes["state"] < 7 else "Default"]

    if session.attributes["state"] == 7:
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that right?"

    elif session.attributes["state"] == 8:
        msg = "Define the following term. " if(session.attributes["termFirst"]) else "What term best fits the following definition? "
        msg += session.attributes["unFamiliar"][0]["term" if(session.attributes["termFirst"]) else "definition"]

    return ("Sorry, I'm having trouble understanding your response... " + msg) if(prefix) else msg

def get_quiz_info(get):
    quizletObject = Quizlet("pzts2bDXSN")
    setArray = quizletObject.search_sets("dog", paged=False)
    if(session.attributes["quizInformation"]["category"] != ""):
        setArray = quizletObject.search_sets(session.attributes["quizInformation"]["category"], paged=False)
        firstSet = setArray["sets"][session.attributes["quizTryCount"]]
        while not isValidQuiz(firstSet):
            session.attributes["quizTryCount"]+= 1
            firstSet = setArray["sets"][session.attributes["quizTryCount"]]
    elif(session.attributes["quizInformation"]["username"] != ""):
        setArray = quizletObject.make_paged_request('users/' + session.attributes["quizInformation"]["username"] + '/sets')[0]
        #catch no sets found here
        max = 0
        for x in range(1, len(setArray)):
            if fuzz.token_set_ratio(setArray[x]["title"], session.attributes["quizInformation"]["title"]) > fuzz.token_set_ratio(setArray[max]["title"], session.attributes["quizInformation"]["title"]):
                max = x
        firstSet = setArray[max]
    set = quizletObject.get_set( firstSet["id"] ) #305754982
    return set[get]

def isValidQuiz(quiz):
    if(
    (quiz["has_images"]) or
    (quiz["visibility"] != "public") or
    (not quiz["has_access"]) or
    (quiz["lang_terms"] != "en") or
    (quiz["lang_definitions"] != "en") ):
        print(quiz["title"])
        return False

    if(
    (session.attributes["quizInformation"]["length"] == "small" and quiz["term_count"] <= 9) or
    (session.attributes["quizInformation"]["length"] == "medium"  and 9 < quiz["term_count"] <= 14) or
    (session.attributes["quizInformation"]["length"] == "large"  and 14 < quiz["term_count"]) ):
        return True
    return False

def shuffle_cards():
    temp = []
    if( len(session.attributes["unFamiliar"]) == 0):
        session.attributes["unFamiliar"] = get_quiz_info("terms")
    while len(session.attributes["unFamiliar"]) > 0:
        temp.append( session.attributes["unFamiliar"].pop(0) )
    while( len(temp) > 0):
        session.attributes["unFamiliar"].append( temp.pop( randint(0, len(temp)-1) ) )

def almostEqual(d1, d2):
    epsilon = 10**(-5)
    return (abs(d2 - d1) < epsilon)

def instantiateNewQuiz():
    session.attributes["unFamiliar"] = []
    session.attributes["familiar"] = []

    session.attributes["quizTryCount"] = 0
    session.attributes["wrongAnswers"] = 0

    session.attributes["quizInformation"] = dict()
    #default values:
    session.attributes["quizInformation"]["QuizPath"] = "" #browse or specific
    session.attributes["quizInformation"]["length"] = "" #Browse - small, medium, or large
    session.attributes["quizInformation"]["category"] = "" #Browse - which category a user wants to browse
    session.attributes["quizInformation"]["username"] = "" #Specific - the username of the owner of a set
    session.attributes["quizInformation"]["title"] = "" #Specific - the name of the specific set

#important note: must implement catches for state 8 in other functions (implement in get_question())

@ask.launch
def WelcomeIntent():
    if "state" in session.attributes:
        prefix = ""
    else:
        session.attributes["state"] = 0
        prefix = "Welcome to Flash Quiz... "
    session.attributes["unFamiliar"] = []
    session.attributes["familiar"] = []

    session.attributes["quizTryCount"] = 0
    session.attributes["wrongAnswers"] = 0

    session.attributes["quizInformation"] = dict()
    #default values:
    session.attributes["quizInformation"]["QuizPath"] = "" #browse or specific
    session.attributes["quizInformation"]["length"] = "" #Browse - small, medium, or large
    session.attributes["quizInformation"]["category"] = "" #Browse - which category a user wants to browse
    session.attributes["quizInformation"]["username"] = "" #Specific - the username of the owner of a set
    session.attributes["quizInformation"]["title"] = "" #Specific - the name of the specific set


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
    #Important States: 2, 5, 7

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
        prefix = "Tell user about some helpful features here... We will now begin the quiz..."
        prefix+= "Define the following term. " if(session.attributes["termFirst"]) else "What term best fits the following definition? "
        msg = prefix + session.attributes["unFamiliar"][0]["term" if(session.attributes["termFirst"]) else "definition"]
    elif almostEqual(session.attributes["state"]%1 , .9): #find a new quiz
        session.attributes["state"] = 0
        session.attributes["quizInformation"] = dict()
        #default values:
        session.attributes["quizInformation"]["QuizPath"] = "" #browse or specific
        session.attributes["quizInformation"]["length"] = "" #Browse - small, medium, or large
        session.attributes["quizInformation"]["category"] = "" #Browse - which category a user wants to browse
        session.attributes["quizInformation"]["username"] = "" #Specific - the username of the owner of a set
        session.attributes["quizInformation"]["title"] = "" #Specific - the name of the specific set
        msg = get_question()
    elif almostEqual(session.attributes["state"]%1 , .8): #restart quiz
        session.attributes["state"] = 8
        session.attributes["quizTryCount"] = 0
        session.attributes["wrongAnswers"] = 0
        session.attributes["unFamiliar"].extend(session.attributes["familiar"].copy())
        session.attributes["familiar"] = []
        shuffle_cards()
        msg = "Restarting set now! " + get_question()
    else:
        msg = get_question(prefix=True)
    return question(msg)

@ask.intent("NoIntent") #Sample utterance: "NO"
def NoIntent():
    #Important States: 2, 5, 7, n.9

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
        msg = get_question()
    elif almostEqual(session.attributes["state"]%1 , .9) or almostEqual(session.attributes["state"]%1 , .8): #User says no to finding a new quiz or restarting current quiz
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
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that right?"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("MediumIntent") #Sample utterance: "Medium, Moderate"
def MediumIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "medium"
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that right?"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("LargeIntent") #Sample utterance: "Large, Big, Long"
def LargeIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "large"
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that right?"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("SwitchCardIntent") #Sample utterance: "switch cards, term to definition, definition to term"
def SwitchCardIntent():
    if (session.attributes["state"] == 8):
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["length"] = "large"
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that right?"
    return question( get_question() if(session.attributes["state"] == 7) else get_question(prefix=True) )

@ask.intent("AnswerIntent",  convert={'response': string})
def AnswerIntent(response):
    #Important States: 1, 2,  4, 5, 6,  8

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
        session.attributes["quizInformation"]["username"] = response
        msg = get_question(format=session.attributes["quizInformation"]["username"])
    elif (session.attributes["state"] == 6): #User answers with the name of the set
        session.attributes["state"] = 7
        session.attributes["quizInformation"]["title"] = response
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("created_by") + ". Is that right?"

    elif (session.attributes["state"] == 8):
        #PROCESS THIS LATER setting answer to true or false depending on fuzzywuzzy
        #compare answer
        answer = session.attributes["unFamiliar"][0]["definition" if(session.attributes["termFirst"]) else "term"]
        ratio = fuzz.token_set_ratio(response, answer)
        if(ratio>=85):
            temp = session.attributes["unFamiliar"].pop(0)
            session.attributes["familiar"].append(temp)
            prefix = "Good job, you got that one correct... "
        elif(ratio >= 65):
            prefix = "You were close! Try rephrasing or altering your answer... "
        else:
            prefix = "It looks like you got that one wrong! "
        if( ratio < 85): #the user answered wrong twice
            session.attributes["wrongAnswers"]+=1
            if(session.attributes["wrongAnswers"]%2 == 1):
                prefix += "Try again... "
            else:
                prefix += "The answer we were looking for was " + answer + ". " + " "
                session.attributes["unFamiliar"].append( session.attributes["unFamiliar"].pop(0) )
        if( len(session.attributes["unFamiliar"]) > 0 ):
            prefix += "Define the following term. " if(session.attributes["termFirst"]) else "What term best fits the following definition? "
            msg = prefix + session.attributes["unFamiliar"][0]["term" if(session.attributes["termFirst"]) else "definition"]
        else:
            session.attributes["state"] = 9
            msg =  "You have finished all of the questions for this set. Would you like to quit, retry, or choose a new quiz"
    else:
        msg = get_question(prefix=True)
    return question(msg)


@ask.intent("QuitIntent") #Sample utterance: "QUIT", "END", "STOP"
def QuitIntent():
    msg = "Thank you for using Flash Quiz! Goodbye! "
    feedback = "Great job! " if len(session.attributes["familiar"]) > len(session.attributes["unFamiliar"]) else "Don't forget to keep studying! "
    msg = ("You saw {} terms and have mastered {} terms. "+ str(feedback) ).format(
		  len(session.attributes["familiar"]) + len(session.attributes["unFamiliar"]), len(session.attributes["familiar"]) )
    return statement(msg)


@ask.intent("RedoIntent") #Sample utterances: "REDO", "RETRY", "TRY AGAIN", "RESTART"
def RedoIntent():
    if (session.attributes["state"] == 9): #user wants to redo quiz after finishing current quiz
        session.attributes["state"] = 8
        session.attributes["quizTryCount"] = 0
        session.attributes["wrongAnswers"] = 0
        session.attributes["unFamiliar"].extend(session.attributes["familiar"].copy())
        session.attributes["familiar"] = []
        shuffle_cards()
        msg = "Restarting set now! " + get_question()
    elif(session.attributes["state"] == 8):
        session.attributes["state"] += .8
        msg = "Are you sure you want to restart your quiz?"
    else:
        msg = get_question(prefix=True)
    return question(msg)


@ask.intent("NewQuizIntent") #Sample utterances: "NEW QUIZ", "NEW", "DIFFERENT QUIZ"
def NewQuizIntent():
    if(session.attributes["state"] == 9):
        session.attributes["state"] = 0
        msg = get_question()
    elif(session.attributes["state"] > 0):
        session.attributes["state"] += .9
        msg = "Are you sure you want to search for a new quiz?"
    else:
        msg = get_question(prefix=True)
    return question(msg)

#GOODBYE MESSAGE - implement later
# "Oh dear there seems to be a problem... we should stop playing. I'll see you next time!"
# feedback = "Great job!" if len(session.attributes["mastered"]) > len(session.attributes["seen"]) else "Don't forget to keep studying!"
# msg = ("You saw {} terms, are familiar with {} terms and mastered {} terms. "+ str(feedback) ).format(
# len(session.attributes["seen"]), len(session.attributes["familiar"]), len(session.attributes["mastered"]) )

##########################
if __name__ == "__main__":
    app.run(debug=True)
