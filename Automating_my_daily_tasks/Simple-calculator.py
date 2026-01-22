#AI calculator
"""User can type what calculaiton he needs to do"""

while True:
   msg11= ['+','-','/','*','add','sub','multi','div','division','multiplication','subtraction','addition']
   msg1= f"\nwhat calculation would you like to do? (enter O to see all options) "

   #msg11= ['+','-','/','*','add','sub','multi','div','division','multiplication','subtraction','addition']

   msg12= ['done','exit','quit']

   msg13 = f"\nTo end type = {(" / ".join(msg12))} or Type 'C' to continue: "
   
   msg2= input(msg1)
   msg21 = msg2.lower()

   #Check whether the input is a valid opreator
   while msg21.upper() == 'O':
         #show all options if user enters O
      print(msg11)
      msg22= input(msg1)
      
      if msg22.upper() != 'o':
         break
      elif msg22 != 'o':
         msg21 = msg2.lower()

   if msg21 not in msg11:
      print (f"\nTry again, {msg2} is not a valid opreator")

      msg15=input(msg13).lower()

      if (msg15.upper()== 'C'):
         print("\nStarting program again")
         continue  
      elif(msg15 in msg12):
         print("\nStopping program")
         break
      elif (msg15 not in msg12):
         print("\nInvalid entry, Stopping program")
         break


   msg3= (f"\nWhat numbers woud like to {msg21}?")
   print(msg3)

   #check whether the input is a number 
   while True:
         msg4 = (f"\nfirst number: ")
         msg6= input(msg4)
      
         if not msg6.isdigit():
            print(f"\n{msg6} Is not a number. Write a number")
            continue


         while True:
            msg5= (f"\nsecnond number: ")
            msg7= input(msg5)
            
            if not msg7.isdigit():
               print(f"\n{msg7} Is not a number. Write a number")
               continue
            else:
               break
         
         break      


   #functions for calculations
   def add(a,b):
      ad=int (a) + int(b)
      return (ad)

   def subtract (c,d):
      sb = int(c) - int(d)
      return (sb)

   def multi (e,f):
      ml=int(e)*int(f)
      return(ml)

   def div (g,h):
      if (h)==0:
         return "Cannot divide by Zero. try again."
      nl=int(g)/int(h)
      return(nl)
   
   def div (g,h):
      if (h)==0:
         return "Cannot divide by Zero. try again."
      nl=int(g)/int(h)
      return(nl)


   #actual calculations
   if msg21 == '+' or msg21 == 'addition' or msg21=='add':
      print(f"\nYour result is: {add(msg6,msg7)}")

   elif  msg21 == '-' or msg21 == 'subtraction' or msg21=='sub':
      print(f"\nYour result is: {subtract(msg6,msg7)}")

   elif  msg21 == '*' or msg21 == 'multiplication' or msg21=='multi':
      print(f"\nYour result is: {multi(msg6,msg7)}")

   elif  msg21 == '/' or msg21 == 'division' or msg21=='div':
      print(f"\nYour result is: {div(msg6,msg7)}")
   
   #Exiting or contnuing the program
   
   msg14=input(msg13).lower()

   if(msg14 in msg12):
      print("\nStopping program")
      break
   elif(msg14.upper()== 'C'):
      print("\nStarting program again")
      continue
   elif (msg14 not in msg12):
      print("\nInvalid Entry. Stopping program")
      break
   