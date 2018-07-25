@ask.intent("SmallIntent") #Sample utterance: "Small, Tiny, Mini, Short"
def SmallIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        #PROCESS THIS LATER
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("username") + ". Is that right?"
    else:
        msg = "Sorry, I'm having trouble understanding your response... "
    return question(msg)

@ask.intent("MediumIntent") #Sample utterance: "Medium, Moderate"
def MediumIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        #PROCESS THIS LATER
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("username") + ". Is that right?"
    else:
        msg = "Sorry, I'm having trouble understanding your response... "
    return question(msg)

@ask.intent("LargeIntent") #Sample utterance: "Large, Big, Long"
def LargeIntent():
    if (session.attributes["state"] == 3):
        session.attributes["state"] = 7
        #PROCESS THIS LATER
        msg = "This is the quiz: " + get_quiz_info("title") + " by " + get_quiz_info("username") + ". Is that right?"
    else:
        msg = "Sorry, I'm having trouble understanding your response... "
    return question(msg)
