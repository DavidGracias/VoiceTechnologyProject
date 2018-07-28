Alexa Flashcard/Quiz Skill - Carnegie Mellon University

Students / Collaborators
  David Garcia
  Jenna McClellan
  Jazmine Freund
  Natalie Cardenas

States
  0: welcome
  0->1: browse - "What type of quiz are you looking to study off of?"
  1->2: browse - "You said {}, is this correct?. "
  2->3: browse - "What size study set do you want? Small, Medium or Large?"
  3->7:
  0->4: specific - "What is the username of the owner of the set?"
  4->5: specific - "You said {}, is this correct?. "
  5->6: specific - "What is the name of the set you are looking for?"
  6->7:
  7: "Is this the right quiz?"
  8: *read question* and takes user's answer
  9: Quiz is finished
  n.8: Restart current quiz
  n.9: Find new quiz

  Session Attributes:
    state - int
          keeps track of the state of the program
    unFamiliar - list
          keeps track of unfamiliar terms
    familiar - list
          keeps track of familiar terms
    lastResponse - string
          keeps track of previous response
    quizTryCount - int
          keeps track of backup quizzes if user rejects first provided quiz
    termFirst - boolean
          keeps track of the side of the card being read
    quizInfo1 - string
          keeps track of quiz type or username
    quizInfo2 - string
          keeps track of length or set name

Quiz Info
  Specific
    0: Username
    1: Set Name
  Browse
    0: Set Type
    1: Set Length

Intents
  WelcomeIntent()
  SpecificIntent()
  BrowseIntent()
  YesIntent()
  NoIntent()
  AnswerIntent()
  QuitIntent()
  RedoIntent()
  NewQuizIntent()


Card types
  unFamiliar
  Familiar

Features
  Shuffle Deck
  Go Back to Last Card
  Skip Card
  Repeat (repeat what Alexa last said)
  New Quiz
  Redo Quiz
  Quit the skill
  Flip the card
  Next Quiz - auto quiz
