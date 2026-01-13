bicycles=['trek','cannondale','redline','specialized']
print(bicycles)

bicycles.append ('Hercules')#append-add a new item to the end of list
print(bicycles)

bicycles[1]='Hero' #replace element
print(bicycles[1].title())

print(bicycles[-1])#returns last item

motor=[]    #Building lists
motor.append('ford')
motor.append('toyota')
motor.append('suzuki')
print(f'This are all the car brands in our garage', motor)


motor.insert(0,'GMC')#inserting element in lists
print(motor)


del motor[3] #deleting a element from the list
print(motor,'\n')


motorcycles = ['honda', 'yamaha', 'suzuki'] #Remove item using pop() method

print(motorcycles.pop(),'\n')
print(motorcycles,'\n')

Fst_own=motorcycles.pop(1) #pop any position

print(f'The first bike that i owned was {Fst_own.title()}\n')

####Execerises
msg= f"My first bicycle was {bicycles[3].title()}"
print(msg)

names=['aakash','dhawal','akash']
print(names[0],names[1],names[2])

msg1 = f'I play cricket with'
print(msg1, names[0])
print(msg1,names[1])
print(msg1,names[2])

