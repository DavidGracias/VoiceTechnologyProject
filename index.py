# Carnegie Mellon SAMS Alexa course - Flash Quiz Project
# adapted from:
# https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/flask-ask-a-new-python-framework-for-rapid-alexa-skills-kit-development
# [20170711} (air) Initial version
#
# Student(s): David Garcia, Jenna McClellan, Jazmine Freund, Natalie Cardenas
#
# <comment on your features>
#

import sys
import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from QuizletAPI import *
from fuzzywuzzy import fuzz, process

app = Flask(__name__)
ask = Ask(app, "/")
# logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# helper function
def get_question():
    if session.attributes["state"] == 0:
        return "Do you want to search or browse for a specific set?"
    elif session.attributes["state"] == 1:
        return "What type of quiz are you looking to study off of?"
    elif session.attributes["state"] == 2:
        return "You said {}, is this correct?. "
    elif session.attributes["state"] == 3:
        return "What size study set do you want? Small, Medium or Large?"

    elif session.attributes["state"] == 4:
        return "What is the username of the owner of the set?"
    elif session.attributes["state"] == 5:
        return "You said {}, is this correct?. "
    elif session.attributes["state"] == 6:
        return "What is the name of the set you are looking for?"
    elif session.attributes["state"] == 7:
        setArray = session.attributes["Quizlet"].search_sets("dog", paged=False)
        h = setArray["sets"][0]
        g = session.attributes["Quizlet"].get_set( h["id"] )

        session.attributes["quizInfo2"] = response
        msg = "This is the quiz: " + g["title"] + ". Is that right?"
        return msg


@ask.launch
def WelcomeIntent():
    if "state" in session.attributes:
        prefix = ""
    else:
        session.attributes["state"] = 0
        prefix = "Welcome to the Flash Quiz... "
    session.attributes["Quizlet"] = Quizlet("pzts2bDXSN")
    session.attributes["unFamiliar"] = []
    session.attributes["familiar"] = []
    #session.attributes["quizIDs"] = []

    msg = prefix + "Do you want to search or browse for a specific set?"
    return question(msg)


@ask.intent("BrowseIntent") #Basic utterance: "browse"
def BrowseIntent():
    if(session.attributes["state"] == 0):
        session.attributes["state"] = 1
        msg = "What type of quiz are you looking to study off of?"
    else:
        msg = get_question()
    return question(msg)

@ask.intent("SpecificIntent") #Basic utterance: "specific"
def SpecificIntent():
    if(session.attributes["state"] == 0):
        session.attributes["state"] = 4
        msg = "What is the username of the owner of the set?"
    else:
        msg = get_question()
    return question(msg)



@ask.intent("YesIntent") #Basic utterance: "YES"
def YesIntent():
    if (session.attributes["state"] == 0):
        msg = "Please say... specific... to search for a specific set, or... browse... to search among all sets on Quizlet"
    elif (session.attributes["state"] == 1):
        msg = "What type of quiz are you looking to study off of?"
    elif (session.attributes["state"] == 2):
        #PROCESS THIS LATER
        # quiz type
        # update quiz info 1 if needed
        session.attributes["state"] = 3
        msg = "What size study set do you want? Small, Medium or Large?"
    elif (session.attributes["state"] == 3):
        msg = "What size study set do you want? Small, Medium or Large?"
    elif (session.attributes["state"] == 4):
        msg = "What is the username of the owner of the set?"
    elif (session.attributes["state"] == 5):
        session.attributes["state"] = 6
        msg = "What is the name of the set you are looking for?"
    elif (session.attributes["state"] == 6):
        msg = "What is the name of the set you are looking for?"
    elif (session.attributes["state"] == 7):
        session.attributes["state"] = 8
        setArray = session.attributes["Quizlet"].search_sets("dog", paged=False)
        h = setArray["sets"][0]
        session.attributes["unFamiliar"] = session.attributes["Quizlet"].get_set( h["id"] )

        msg = session.attributes["unFamiliar"]["terms"][0]["definition"] #what session is this
    else:
        msg = ""
        #session.attributes["state"]s
    if(session.attributes["state"] == 0) or (session.attributes["state"] == 1) or (session.attributes["state"] == 3)  or (session.attributes["state"] == 4) or (session.attributes["state"] == 6):
        msg = "Sorry, I'm having trouble understanding your response... " + msg
    return question(msg)

@ask.intent("NoIntent") #Basic utterance: "NO"
def NoIntent():
    if (session.attributes["state"] == 0): #Goodbye Message #I don't think you understood the question
        msg = "Please say... specific... to search for a specific set, or... browse... to search among all sets on Quizlet"
    elif (session.attributes["state"] == 1): #
        msg = "What type of quiz are you looking to study off of?"
    elif (session.attributes["state"] == 2): #
            session.attributes["state"] = 1
            msg = "What type of quiz are you looking to study off of?"
    elif (session.attributes["state"] == 3):  #After playing
        msg = "What size study set do you want? Small, Medium or Large?"
    elif (session.attributes["state"] == 4):
        msg = "What is the username of the owner of the set?"
    elif (session.attributes["state"] == 5):
        session.attributes["state"] = 4
        msg = "What is the username of the owner of the set?"
    elif (session.attributes["state"] == 6):
        msg = "What is the name of the set you are looking for?"
    elif (session.attributes["state"] == 7):
        setArray = session.attributes["Quizlet"].search_sets("dog", paged=False)
        h = setArray["sets"][0]
        g = session.attributes["Quizlet"].get_set( h["id"] )

        session.attributes["quizInfo2"] = response
        msg = "This is the quiz: " + g["title"] + ". Is that right?"
    else:
        msg = "Oh dear there seems to be a problem... we should stop playing. I'll see you next time!"
        """
            feedback = "Great job!" if len(session.attributes["mastered"]) > len(session.attributes["seen"]) else "Don't forget to keep studying!"
            msg = ("You saw {} terms, are familiar with {} terms and mastered {} terms. "+ str(feedback) ).format(
     		len(session.attributes["seen"]), len(session.attributes["familiar"]), len(session.attributes["mastered"]) )
        """
    if(session.attributes["state"] == 0) or (session.attributes["state"] == 1) or (session.attributes["state"] == 3)  or (session.attributes["state"] == 4) or (session.attributes["state"] == 6):
        msg = "Sorry, I'm having trouble understanding your response... " + msg
    return question(msg)


@ask.intent("AnswerIntent", convert={"response": string})
def answer(response):
    #Choose Path
    if (session.attributes["state"] == 0): #didn't recognize SpecificIntent or BrowseIntent
        #browse / specific
        msg = "Please say specific to search for a specific set, or browse to search among all sets"

    #Path: Browse
    elif (session.attributes["state"] == 1):
        session.attributes["state"] = 2
        #PROCESS THIS LATER response and analyze what type of quiz they want

        session.attributes["quizInfo1"] = response
        msg = ("You said {}, is this correct?. ").format(response)
    elif (session.attributes["state"] == 2):
        session.attributes["state"] = 1
        msg = "What type of quiz are you looking to study off of?"
    elif (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        #PROCCESS THIS LATER
        #Do you want to do this quiz jawn
        #quizInfo1
        #quizInfo2=
        session.attributes["state"] = 7
        setArray = session.attributes["Quizlet"].search_sets("dog", paged=False)
        h = setArray["sets"][0]
        g = session.attributes["Quizlet"].get_set( h["id"] )

        session.attributes["quizInfo2"] = response
        msg = "This is the quiz: " + g["title"] + ". Is that right?"
    #Path: Specific
    elif (session.attributes["state"] == 4):
        session.attributes["state"] = 5
        #PROCESS THIS LATER response and analyze the username of the quiz

        session.attributes["quizInfo1"] = response
        msg = ("You said {}, is this correct?. ").format(response)
    elif (session.attributes["state"] == 5):
        session.attributes["state"] = 4
        msg = "What is the username of the owner of the set?"
    elif (session.attributes["state"] == 6):
        session.attributes["state"] = 7
        setArray = session.attributes["Quizlet"].search_sets("dog", paged=False)
        h = setArray["sets"][0]
        g = session.attributes["Quizlet"].get_set( h["id"] )

        session.attributes["quizInfo2"] = response
        msg = "This is the quiz: " + g["title"] + ". Is that right?"
    elif (session.attributes["state"] == 7):
        setArray = session.attributes["Quizlet"].search_sets("dog", paged=False)
        h = setArray["sets"][0]
        g = session.attributes["Quizlet"].get_set( h["id"] )

        session.attributes["quizInfo2"] = response
        msg = "This is the quiz: " + g["title"] + ". Is that right?"

    elif (session.attributes["state"] == 8):
        #PROCESS THIS LATER setting answer to true or false depending on fuxx
        #compare answer
        answer = session.attributes["unFamiliar"]["term"]
        ratio = fuzz.token_set_ratio(response,answer)
        if(ratio>=70):
            temp = session.attributes["unFamiliar"].pop(0)
            session.attributes["familiar"].append(temp)
            msg = "You got it correct! "
        else:
            msg = "You got it wrong! "
        if( len(session.attributes["unFamiliar"]) > 0):
            msg += " Here is the next defintion: " + session.attributes["unFamiliar"][0]["definition"]
        else:
            msg = "You have finished all of the questions for this set. Would you like to quit, retry, or choose a new quiz"

    else:
        session.attributes["state"] = 404
        return statement("Sorry, there was an error processing your request.") #would you like to try again?

    if(session.attributes["state"] == 0)  or (session.attributes["state"] == 5) or (session.attributes["state"] == 6) or (session.attributes["state"] == 7):
        msg = "Sorry, I'm having trouble understanding your response... " + msg
    return question(msg)





@ask.intent("QuitIntent") #Basic utterance: "QUIT", "END", "STOP"
def QuitIntent():
    if (session.attributes["state"] == 8): #user wants to quit after end of quiz
        msg = "Thank you for using Flash Quiz! Goodbye!"
        """
            feedback = "Great job!" if len(session.attributes["mastered"]) > len(session.attributes["seen"]) else "Don't forget to keep studying!"
            msg = ("You saw {} terms, are familiar with {} terms and mastered {} terms. "+ str(feedback) ).format(
     		len(session.attributes["seen"]), len(session.attributes["familiar"]), len(session.attributes["mastered"]) )
        """
        #add code to close skill?
    else:
        msg = "Sorry, I'm having trouble understanding your response..." + msg
    return question(msg)


@ask.intent("RedoIntent") #Basic utterances: "REDO", "RETRY", "TRY AGAIN", "RESTART"
def RedoIntent():
    if (session.attributes["state"] == 8): #user wants to redo quiz after finishing current quiz
        session.attributes["state"] == 6
        msg = "Restarting set now!" #CHANGE MESSAGE to ask first term of restarted set
    else:
        msg = "Sorry, I'm having trouble understanding your response..." + msg
    return question(msg)


@ask.intent("NewQuizIntent") #Basic utterances: "NEW QUIZ", "NEW", "DIFFERENT QUIZ"
def NewQuizIntent():
    if (session.attributes["state"] == 8): #user wants to try a new set after finishing current quiz
        session.attributes["state"] == 0
        msg = "Do you want to search or browse for a specific set?"
    else:
        msg = "Sorry, I'm having trouble understanding your response..." + msg
    return question(msg)


##########################
if __name__ == "__main__":
    app.run(debug=True)
