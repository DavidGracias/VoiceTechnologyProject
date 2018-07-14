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

    session.attributes["unFamiliar"] = []
    session.attributes["familiar"] = []
    #session.attributes["quizIDs"] = []

    msg = prefix + "Do you want to search or browse for a specific set?"
    return question(msg)


@ask.intent("BrowseIntent") #Basic utterance: "browse"
def BrowseIntent():
    session.attributes["state"] = 1
    msg = "What type of quiz are you looking to study off of?"
    return question(msg)

@ask.intent("BrowseLengthIntent", convert={"length": string}) #Basic utterances: "small", "medium", "large"
def BrowseLengthIntent(length):
    #process length
    msg = ("You said {}, is this correct?. ").format(blah)
    return question(msg)

@ask.intent("SpecificIntent") #Basic utterance: "specific"
def SpecificIntent():
    session.attributes["state"] = 3
    msg = "What is the username of the owner of the set"
    return question(msg)



@ask.intent("YesIntent") #Basic utterance: "YES"
def YesIntent():
    if (session.attributes["state"] == 0):
        msg = "Please say... specific... to search for a specific set, or... browse... to search among all sets on Quizlet"
    elif (session.attributes["state"] == 1):
        msg = "What type of quiz are you looking to study off of?"
    elif (session.attributes["state"] == 2):
        session.attributes["state"] == 3
        #process?, and move on
        msg = "What size study set do you want? Small, Medium or Large?"
    elif (session.attributes["state"] == 3):

    elif (session.attributes["state"] == 4):

    else:
        #states 0, 1,
    "Sorry, I'm having trouble understanding your response... "
    return question(msg)

@ask.intent("NoIntent") #Basic utterance: "NO"
def NoIntent():
    if session.attributes["state"] == 0: #Goodbye Message #I don't think you understood the question
        msg = "Please say... specific... to search for a specific set, or... browse... to search among all sets on Quizlet"
    elif session.attributes["state"] == 1: #
        msg = "What type of quiz are you looking to study off of?"
    elif session.attributes["state"] == 2: #
            session.attributes["state"] = 1
            msg = "What type of quiz are you looking to study off of?"
    elif session.attributes["state"] == 3:  #After playing
        feedback = "Great job!" if len(session.attributes["mastered"]) > len(session.attributes["seen"]) else "Don't forget to keep studying!"
        msg = ("You saw {} terms, are familiar with {} terms and mastered {} terms. "+ str(feedback) ).format(
 		len(session.attributes["seen"]), len(session.attributes["familiar"]), len(session.attributes["mastered"]) )

    else:
        msg = "Oh dear there seems to be a problem... we should stop playing. I'll see you next time!"
    "Sorry, I had trouble understanding your response... "
    return statement(msg)


@ask.intent("AnswerIntent", convert={"response": string})
def answer(response):
    #Choose Path
    if (session.attributes["state"] == 0): #didn't recognize SpecificIntent or BrowseIntent
        #browse / specific
        msg = "Please say specific to search for a specific set, or browse to search among all sets"

    #Path: Browse
    elif (session.attributes["state"] == 1):
        session.attributes["state"] == 2
        #process response and analyze what type of quiz they want
        session.attributes[""] = #type of quiz
        msg = ("You said {}, is this correct?. ").format(blah)
    elif (session.attributes["state"] == 2):
        session.attributes["state"] = 1
        msg = "What type of quiz are you looking to study off of?"
    #Path: Specific
    elif (session.attributes["state"] == 3):
        #username
    elif (session.attributes["state"] == 4):
        #set name
    else:
        session.attributes["state"] = 404
        return statement("Sorry, there was an error processing your request.") #would you like to try again?

    "Sorry, I had trouble understanding your response... "
    return question(msg)


##########################
if __name__ == "__main__":
    app.run(debug=True)
