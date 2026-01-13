#Variables, Strings and Simple data types

#print just a string
print ("Hello World")
print ('Hello World')

#print a string with using variable
msg = ("Hello World")
print(msg)

#f-strings(using variable in Strings)
firstname = "alberto"
secondname= "gomez"
fullname=f"{firstname} {secondname}"
print(fullname.title())

#changing case
print(firstname.title())
print(fullname.capitalize())
print(fullname.upper())
print(fullname.lower())

# Stripping whitespace
fav_lang=' python '
print(fav_lang.lstrip()) #left space trim
print(fav_lang.rstrip()) #right space trim
print(fav_lang.strip()) #trim space from both end

#Adding tabs 
print("\tSagar") # \t to add tab space
print("\nPython\nC\nJava") #\n add to a new line

#Removing prefixes
url = 'https://nostarch.com'
print(url.removeprefix('https://')) #remove prefix
print(url.removesuffix('starch.com')) #remove suffix

#Numbers
a,b,c=1,2,3
print(a)

#Integers
add = 2+3
print(add)

Subtract = 9-3
print(Subtract)

Mutli = 2*3
print(Mutli)

float = 1.2 + 4.7
print(float)

divide = 12/4
print (divide)

#Multiple assignment of numbers
x,y,z=1,2,3

#constans - using capital letters
MAX_CONNEC=5000

#import this // Zen of python
#---------------------------------------------------------------------
#Lists
bicycles =['trek','cannondale', 'redline','specialized']
print(*bicycles) # * adding star or splat open the list , it will jus print all the values from the list. 

#accessing elements
cycle_1=bicycles[0] #accssing element using number 0,1,2,3. numbers represent the items from the list 
print(cycle_1.title())

print(cycle_1[-1]) #returns the last item from the list

print(f'My first bicycle is {bicycles[3].upper()}') #using f strings with individual Values from a list.


#Modifiying elements in a list
Motorcycles =['honda','Ducati','suzuki'] #simple list
print(Motorcycles)

Motorcycles[1] ='yamaha' #change item in a list based on index
print (Motorcycles)

Motorcycles.append('bajaj') #adds new item at the of the list
print(*Motorcycles)

#Inserting elements into a list

Motorcycles.insert(0,'hero')
print (Motorcycles)

#Removing Elements from a list using pop()
del Motorcycles[1] #deleting item from the list
print(Motorcycles)

pop_motor=Motorcycles.pop() #pop removes the last item from the list. Then print the last time, using the variable
print(pop_motor)

first_bike = Motorcycles.pop(1) #pop item from any position from a list
print(first_bike)

#Remove an item by value
print(Motorcycles)

Motorcycles.remove('suzuki')
print(Motorcycles)

#Sorting a list
cars =['bmw','ford','audi','toyota','subaru']
cars.sort() #sorts the list permanently in alphabetical order
print(cars)

cars.sort(reverse=True) #sorts the list permanently in alphabetical order in reverse
print(cars)

print(sorted(cars)) #sorted function temporaily sorts the list. it keeps the original list

cars.reverse() #print list in reverse order
print(cars)

#Finding the length of a list
len(cars)
print(len(cars))

#looping through a list
magician =['alice','david','carol']
for i in magician:
    print(f"{i.capitalize()}, that was a great trick ")


# Range() function- prints a series of numbers
for value in range(0,6):
    print(value)

#using range() to make a list of numbers
numbers = list(range(0,9))
print(numbers)    


#loan
Pa = 12013
plan = 1064*12

Final= plan - Pa
print(f'Total amount paid for 12 month {plan}, extra amount paid {Final}')

#using range() in function
for val in range(1,9):
    print(val)

#list comprehensions - allows you to generate same listin just one line of code. it combines the for loop and the 
#creation of the new elements into ine line and automatically appends each new element.
squares=[value**2 for value in range(1,11)]
print(squares)

#slicing a list
players = ['charles', 'martina', 'michael', 'florence', 'eli']
print(players[0:3])

for p in players[:3]: #looping through a list
    print(p.title())

pla = players[:] #copying a list
print (pla)

#Tuple #looks like a list, it has parentheses instead of square brackets
dim =(2,50)
print(dim[0])

for d in dim:
    print(d)

dim = (40,90) # writing over a tuple
print(dim)    

#If statements
cars = ['audi', 'bmw', 'subaru', 'toyota']

for car in cars:       #loop thru lists and with if statements verify if a item is found then do something
    if car == 'bmw':
        print(car.upper())
    else:
        print(car.title())    

#checking that a list is not empty
requested_toppings = []
if requested_toppings:  
    for requested_topping in requested_toppings:
        print(f"Adding {requested_topping}.")
    print("\nFinished making your pizza!")
else:
    print("Are you sure you want a plain pizza?")       


#Dictionaries
# allows you to connect pieces of information

# A simple Dictionary
alien_0 ={'color':'green','points':5}
print(alien_0['color']) #Accessing the values in a dictionary
print(alien_0['points'])

alien_0['x_posi'] = 0 #adding New Key-Value Pairs
alien_0['y_posi'] = 25

print(alien_0)

alien_0['color']= 'yellow' #Modifying the values in a Dictionary
print(alien_0)

del alien_0['points'] #Removing Key-Value Pairs

col =alien_0['color'].title()
print(f"My Favorite color is {col}")

user_0 = {
'username': 'efermi',
'first': 'enrico',
'last': 'fermi',
}

#Looping Through all Key-Value Pairs
for k, v in user_0.items():
    print (f"\nKey:{k}")
    print (f"Value: {v}")

#Looping through All the keys in a Dictionary
for name in user_0.keys():
    print(name.title())


#input 
#name = input("Tell your name ")
#print (f"\nHello, {name}")

#while loops
cnum = 1
while cnum>5:
    print(cnum)
    cnum +=1


# prompt = "\nTell me something, and I will repeat it back to you:"
# prompt += "\nEnter 'quit' to end the program. "
# msg12 = ""
# while msg12 != 'quit':
#     message= input(prompt)
#     msg12 = message.lower()
#     print(msg12)   

#Functions
def greet_user(username):
    msg33 = username.lower()
    if msg33 == "dragon":
        print ("Sorry I cant print that name")
    else:
        return msg33.title() #return values
        
    

name23 = greet_user(username="Dr.sagar")        
print (name23)

#Return Values
#making an argument optional
def formatname (fname,laname,mname=''):
    if mname:
        fname = f"{fname} {mname} {laname}"
    else:
        fname = f"{fname} {laname}"    
    return fname.title()

#Returning a Dictionary
def build_person(first_name, last_name):
#Return a dictionary of information about a person
    person = {'first': first_name, 'last': last_name}
    return person

#using a Function with a While Loop
# This is an infinite loop!
# while True:
#     print("\nPlease tell me your name:")
#     f_name = input("First name: ")
#     l_name = input("Last name: ")
#     formatted_name = build_person(f_name, l_name)
#     print(f"\nHello, {formatted_name}!")



#passing a list
def countlist (names):
    count = 0
    for name in names:
        count +=1
    print(count)        


Match_1=['Ravee Karnati', 'Shubh Mahapatra', 'Dhawal Shah', 'Madan Galla', 'Yogen Chauhan', 'Aditya Bhattacharya', 'Sagar Pawaskar', 'anil baid', 'Vidya Dwivedi', 'Umang Chauhan', 'Dhiraj Adhikari']
countlist(Match_1)

#Passing an Arbitrary Number of Arguments
def make_pizza(*toppings):
#"""Print the list of toppings that have been requested."""
    print(toppings)


make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')

#Mixing Positional and Arbitrary Arguments
def make1_pizza(size, *toppings):
    print("jhappt")

#Using Arbitrary Keyword Arguments        
def build_profile(first, last, **user_info):
#"""Build a dictionary containing everything we know about a user."""
    user_info['first_name'] = first
    user_info['last_name'] = last
    return user_info

user_profile = build_profile('albert', 'einstein',
                            location='princeton',
                            field='physics')
print(user_profile)

#importing an Entire module

# import pizza 
#pizza.make_pizza(16, 'pepperoni')
#pizza.make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')

#importing specific Functions
# from module_name import function_name

# You can import as many functions as you want from a module by separating
# each function’s name with a comma:
# from module_name import function_0, function_1, function_2

#using as to give a functionan Alias
# from pizza import make_pizza as mp
# mp(16, 'pepperoni')
# mp(12, 'mushrooms', 'green peppers', 'extra cheese')

#Using as to Give a module an alias
# import pizza as p
# p.make_pizza(16, 'pepperoni')
# p.make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')

#Importing all functions in a Module
# from pizza import *
# make_pizza(16, 'pepperoni')
# make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')