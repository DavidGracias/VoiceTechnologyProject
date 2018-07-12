#
# SAMS Alexa course -- first Skill
# This skill allows you to play the memory game multiple times
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


# helper function: create a number sequence, embed in a challenge, rerutn
def make_game():
    msg = "I was here"
    
    numbers = [randint(0, 9) for _ in range(session.attributes["long"])]
    msg = render_template("round", numbers=numbers)
    session.attributes["numbers"] = numbers[::-1]  # reverse
    session.attributes["game"] += 1  # game counter
    
    return(msg)


# States
#
# 0: welcome()
# 1: 

@ask.launch
def welcome():
    if "welcome" in session.attributes:
        prefix = ""
    else:
        session.attributes["intro"] = 1
        prefix = "Welcome to the Flash Quiz..."
    session.attributes["state"] = 0  # conversation state we were just in
    
    msg = prefix + " Do you want to search for a specific set or browse?"
    return question(msg)


@ask.intent("NoIntent")
def goodbye():
    if session.attributes["state"] == 0:
        msg = "Ah well, you could have learned so much ... Goodbye."
    
    # the user played; give them some feedback on their performance
    elif session.attributes["state"] == 3:  # origin state
        msg = "You played {}, and won, {}. Good job!".format(
 		session.attributes["game"], session.attributes["win"])
        session.attributes["state"] = 4  # set current state
        sys.stderr.write("-----------------------[NEW state]----> "+str(session.attributes["state"])+"\n")
        sys.stderr.flush()

    else:
        msg = "oh dear... we should stop playing."

        # starement() says something then exists immediately
    return statement(msg)


# NoIntent (a "yes") can be a response to several originating states;
# use the (previous) state to select the right one
@ask.intent("YesIntent")
def next_round():
    #dispatch per the originating state; for now state 2,3 "yes" works
    sys.stderr.write("\n-----------------------[OLD state]----> "+str(session.attributes["state"])+"\n")
    sys.stderr.flush()
    
    # when it"s user turn to play to play
    if (session.attributes["state"] == 1) or (session.attributes["state"] == 3):
        msg = make_game()
        
        session.attributes["state"] = 2  # current (this) state
        sys.stderr.write("-----------------------[NEW state]----> "+str(session.attributes["state"])+"\n")
        sys.stderr.flush()
        return question(msg)


@ask.intent("AnswerIntent", convert={"first": int, "second": int, "third": int})
def answer(first, second, third):

    sys.stderr.write("\n-----------------------[OLD state]----> "+
	str(session.attributes["state"])+
	"\n")
    sys.stderr.flush()

    # create the correct answer sequence
    winning_numbers = session.attributes["numbers"]
    # was the sequence 2 long?
    if session.attributes["long"] == 2:
        # score it and feedback
        if [first, second] == winning_numbers:
            msg = render_template("win")
            session.attributes["win"] += 1  # win counter
        else:
            msg = render_template("lose")
    # was the sequence 3 long?
    elif session.attributes["long"] == 3:
        # score it and feedback
        if [first, second, third] == winning_numbers:
            msg = render_template("win")
            session.attributes["win"] += 1  # win counter
        else:
            msg = render_template("lose")
    # code here for anything longer...

    session.attributes["state"] = 3  # set current state
    sys.stderr.write("-----------------------[NEW state]----> "+str(session.attributes["state"])+"\n")
    sys.stderr.flush()
    return question(msg+"... Do you want to keep playing?")


##########################
if __name__ == "__main__":
    app.run(debug=True)

#
