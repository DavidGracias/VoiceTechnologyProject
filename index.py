# Hello World
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
    session.attributes["state"] = 0
    session.attributes["unseen"] = []
    session.attributes["seen"] = []
    session.attributes["familiar"] = []
    session.attributes["mastered"] = []
    if "welcome" in session.attributes:
        prefix = ""
    else:
        session.attributes["welcome"] = 1
        prefix = "Welcome to the Flash Quiz..."

    msg = prefix + " Do you want to search or browse for a specific set?"
    return question(msg)


@ask.intent("SpecificIntent")
def SpecificIntent(): #specific state
    session.attributes["state"] = 1
    msg = ""
    return question(msg)


@ask.intent("BrowseIntent")
def BrowseIntent(): #browse state
    session.attributes["state"] = 2
    msg = ""
    return question(msg)





@ask.intent("NoIntent")
def NoIntent():
    if session.attributes["state"] == 0: #Goodbye Message
        msg = "Ah well, you could have learned so much ... Goodbye."

    elif session.attributes["state"] == 1: #

    elif session.attributes["state"] == 2: #


    elif session.attributes["state"] == 3:  #After playing
        feedback = "Great job!" if len(session.attributes["mastered"]) > len(session.attributes["seen"]) else "Don't forget to keep studying!"
        msg = ("You saw {} terms, are familiar with {} terms and mastered {} terms. "+ str(feedback) ).format(
 		len(session.attributes["seen"]), len(session.attributes["familiar"]), len(session.attributes["mastered"]) )

    else:
        msg = "Oh dear there seems to be a problem... we should stop playing. I'll see you next time!"
    return statement(msg)




@ask.intent("YesIntent")
def YesIntent():
    if (session.attributes["state"] == 1):

    elif (session.attributes["state"] == 2):

    elif (session.attributes["state"] == 3):

    elif (session.attributes["state"] == 4):

    return question(msg)


@ask.intent("AnswerIntent", convert={"first": int, "second": int, "third": int})
def answer(first, second, third):
    #session.attributes["state"] =

    return question(msg+"... Do you want to keep playing?")


##########################
if __name__ == "__main__":
    app.run(debug=True)
