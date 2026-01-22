#Calculate the expenses for Mega Samash 2025

#Goal= Count players who played, how many total games.

#Name of players , who played the matches 
Match_1 = 'Ravee Karnati', 'Shubh Mahapatra', 'Dhawal Shah', 'Madan Galla', 'Yogen Chauhan', 'Aditya Bhattacharya', 'Sagar Pawaskar', 'anil baid', 'Vidya Dwivedi', 'Umang Chauhan', 'Dhiraj Adhikari'

Match_2 = 'Yogen Chauhan', 'Ravee Karnati', 'Sagar Pawaskar', 'Umang Chauhan', 'Jay Trivedi', 'Madan Galla', 'Dhawal Shah', 'Gaurav dhar', 'Mehul Patel', 'Aakash Bhansali', 'Srinivasan Purushothaman'

Match_3 = 'Ravee Karnati', 'Yogen Chauhan', 'Mehul Patel', 'Madan Galla', 'Sagar Pawaskar', 'Jay Trivedi', 'Gaurav dhar', 'Aakash Bhansali', 'Umang Chauhan', 'Vidya Dwivedi', 'Aditya Bhattacharya', 'Dhawal Shah'

Match_4 = 'Ravee Karnati', 'Yogen Chauhan', 'Aditya Bhattacharya', 'Gaurav dhar', 'Madan Galla', 'Piyank Patel', 'Ankur Bajaj', 'Vidya Dwivedi', 'Mehul Patel', 'Ankit Gupta', 'Umang Chauhan'

Match_5 = 'Ravee Karnati', 'Yogen Chauhan', 'Shubh Mahapatra', 'Gaurav dhar', 'Dhawal Shah', 'Sagar Pawaskar', 'Madan Galla', 'Jay Trivedi', 'Aditya Bhattacharya', 'Aakash Bhansali', 'Mehul Patel'

Match_6 = 'Ravee Karnati', 'Dhawal Shah', 'Madan Galla', 'Yogen Chauhan', 'Sagar Pawaskar', 'Gaurav dhar', 'Vidya Dwivedi', 'Jay Trivedi', 'Ankur Bajaj', 'Mehul Patel', 'Sudhir goud Rallabandi'

Match_7 = 'Ravee Karnati', 'Dhawal Shah', 'Madan Galla', 'anil baid', 'Gaurav dhar', 'Ankur Bajaj', 'Sagar Pawaskar', 'Aditya Bhattacharya', 'Shubh Mahapatra', 'Vidya Dwivedi', 'Sudhir goud Rallabandi'

Match_8 = 'Ravee Karnati', 'Dhawal Shah', 'Mehul Patel', 'anil baid', 'Shubh Mahapatra', 'Madan Galla', 'Yogen Chauhan', 'Jay Trivedi', 'Niraj Bhatt', 'Ankur Bajaj', 'Gaurav dhar'

Match_9 = 'Ravee Karnati', 'Shubh Mahapatra', 'Aditya Bhattacharya', 'Yogen Chauhan', 'Gaurav dhar', 'Madan Galla', 'Mehul Patel', 'Sagar Pawaskar', 'Jay Trivedi', 'Umang Chauhan', 'Vidya Dwivedi'

Match_10 = 'Yogen Chauhan', 'Jay Trivedi', 'Ravee Karnati', 'Dhawal Shah', 'Viraj Patel', 'Gaurav dhar', 'Madan Galla', 'Shubh Mahapatra', 'Aditya Bhattacharya', 'Sagar Pawaskar', 'Umang Chauhan'

Match_11 = 'Yogen Chauhan', 'Gaurav dhar', 'Dhawal Shah', 'Sagar Pawaskar', 'Ravee Karnati', 'Madan Galla', 'Mehul Patel', 'Viraj Patel', 'Jay Trivedi', 'Aditya Bhattacharya'



#Need to find how many matches each player has played.
ALL = [Match_1,Match_2,Match_3,Match_4,Match_5,Match_6,Match_7,Match_8,Match_9,Match_10,Match_11]
Dic = {
    "Match 1" : Match_1
}

#This int count of the player who played matches
#player_count = 0
match_count = 0

#msg that will be shown to the user
msg1= "Welcome to player/match counter\n Which player's matches would you like to count : "

#With input the msg1 is shown to the user and then user input is storeed in the variable msg2
msg2= input(msg1) 

#Remove spaces and case-senstivity from the names
player_name = msg2.strip().casefold() 

#Loop thru the list ALL to find name in all matches
for a in ALL: #this loop will go thru all the elements of list ALL
    for b in a: #Here it goes thru values of each list elements. 
        if b.casefold().startswith(player_name): #Here it trys to find the name in each element
           match_count +=1  #add the match counts 
           acname = b  #if the name is found it stores it in variable acname
           
        #print(f"{acname} played in match {match_count}")

#total               
print(f"{acname} played in total of {match_count} matches")