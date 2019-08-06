age = 45

name = 'Gio' 

print ("my name is {} and I am {}".format (name,age))

# comment



if age > 18:
    print ("you are older than 18")
else:    
    print ("you are older than 18")


numbers = [76, 83, 16, 69, 52, 78, 10, 77, 45, 52, 32, 17, 58, 54, 79, 72, 55, 50, 81, 74, 45, 33, 38, 10, 40, 44, 70, 81, 79, 28, 83, 41, 14, 16, 27, 38, 20, 84, 24, 50, 59, 71, 1, 13, 56, 91, 29, 54, 65, 23, 60, 57, 13, 39, 58, 94, 94, 42, 46, 58, 59, 29, 69, 60, 83, 9, 83, 5, 64, 70, 55, 89, 67, 89, 70, 8, 90, 17, 48, 17, 94, 18, 98, 72, 96, 26, 13, 7, 58, 67, 38, 48, 43, 98, 65, 8, 74, 44, 92]

for num in numbers:
    if (num > 90):
        print(num) 

dogs ={"fido":8,"sally":17,"sean":2}

print (dogs["sally"])

words = ["PoGo","Spange","Lie-Fi"]
definitions = ["Slang for Pokemon Go","To collect spare change, either from couches, passerbys on the street or any numerous other ways and means","When your phone or tablet indicates that you are connected to a wireless network, however you are still unable to load webpages or use any internet services with your device"] 
cooldictionary = {words[0]:definitions[0],words[1]:definitions[1],words[2]:definitions[2] }


class Dog:
    def bark(self):
        print("bark")

mydog = Dog()
mydog.bark()
mydog.name = "Fido"
mydog.age = "16"

print(mydog.name)
print(mydog.age)


class Cat:
    def __init__(self,name,age,furcolor):
        self.name = name
        self.age = age
        self.furcolor = furcolor


mycat = Cat("michon",12,"taby")
print (mycat.name)

# djangoproject.com is the reference
# i installed with conda install django
# my conda environment is djangoCourse
# open it with: conda activate djangoCourse

# my new project 
# django-admin startproject wordcount

# start with (in folder where project was created)
# python3 manage.py  runserver
