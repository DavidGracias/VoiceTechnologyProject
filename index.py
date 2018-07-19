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

app = Flask(__name__)
ask = Ask(app, "/")
# logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# helper function
def helper_function():
    return 42


@ask.launch
def WelcomeIntent():
    if "state" in session.attributes:
        prefix = ""
    else:
        session.attributes["state"] = 0
        prefix = "Welcome to the Flash Quiz... "
    #session.attributes["Quizlet"] = Quizlet("pzts2bDXSN")
    #session.attributes["unFamiliar"] = []
    #session.attributes["familiar"] = []
    #session.attributes["quizIDs"] = []

    msg = prefix + "Do you want to search or browse for a specific set?"
    return question(msg)


@ask.intent("BrowseIntent") #Basic utterance: "browse"
def BrowseIntent():
    if(session.attributes["state"] == 0):
        session.attributes["state"] = 1
        msg = "What type of quiz are you looking to study off of?"
    else:
        msg = "" # catch this intent
    return question(msg)

@ask.intent("BrowseLengthIntent", convert={"length": string}) #Basic utterances: "small", "medium", "large"
def BrowseLengthIntent(length):
    session.attributes["quizInfo2"] = length
    if(session.attributes["state"] == 3):
        session.attributes["state"] = 7
        #PROCCESS THIS LATER
        #Do you want to do this quiz jawn
        #quizInfo1
        #quizInfo2
        msg = ""
    else:
        msg = "" # catch this intent
    return question(msg)

@ask.intent("SpecificIntent") #Basic utterance: "specific"
def SpecificIntent():
    if(session.attributes["state"] == 0):
        session.attributes["state"] = 4
        msg = "What is the username of the owner of the set?"
    else:
        msg = "" # catch this intent
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
        msg = "" #what session is this
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
        msg = ""
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
        msg = "What size study set do you want? Small, Medium or Large?"

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
        #PROCESS THIS LATER response and analyze the username of the quiz

        session.attributes["quizInfo2"] = response
        msg = ("You said {}, is this correct?. ").format(response)
    else:
        session.attributes["state"] = 404
        return statement("Sorry, there was an error processing your request.") #would you like to try again?

    if(session.attributes["state"] == 0) or (session.attributes["state"] == 3)  or (session.attributes["state"] == 5) or (session.attributes["state"] == 6):
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
