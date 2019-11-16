import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')

""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate

engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

#engine.setProperty('voice', u'spanish-us')
#engine.setProperty('voice', u'english+f1')
engine.setProperty('voice', u'english+f4')


#engine.say("Hola Simon! como estas, te quiero mucho")
#engine.say("Hi Nicole. this is the robot, how are you doing today?")


#engine.say("Hi Simon. I am a robot, Would you like to dance?")
#engine.say("Hey Simon. Where is papa's phone, bring it upstairs please")

#engine.say("No google,  jump and wave your hands,do  you like dancing?")
#engine.say("Hey Simon, bring me the a blue car please? ")

engine.say("Hey Simon, go get your pijamas please? ")

engine.runAndWait()
engine.stop()