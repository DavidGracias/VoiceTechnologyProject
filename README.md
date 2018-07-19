Alexa Flashcard/Quiz Skill - Carnegie Mellon University

Students / Collaborators
  David Garcia
  Jenna McClellan
  Jazmine Freund
  Natalie Cardenas

States
  0: welcome
  1: browse - type
  2: browse - length
  3: specific - username
  4: specific - set name
  5: set is chosen
  6: user answer - first
  7: user answer - second
  8: end of set
  9: exit check state

  Session Attributes:
    state - int
          keeps track of the state of the program
    unFamiliar - list
          keeps track of unfamiliar terms
    familiar - list
          keeps track of familiar terms
    lastResponse - string
          keeps track of previous response
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
