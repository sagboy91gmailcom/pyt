# Python Practice Set (NO ANSWERS) — Variables, Data Types, Strings, Lists
# ------------------------------------------------------------------------
# Instructions
# - Write your code ONLY where it says 'YOUR CODE HERE'.
# - Do not add printouts of expected results; try the logic yourself.
# - When you're done, run:  python practice_set_no_answers.py
# - Share this file (or paste code) with me to review and give feedback.
#
# Tip: Keep solutions minimal and readable. Use f-strings where formatting is needed.

# ====================== VARIABLES ======================

# Q1) Create variables for your name (str), age (int), and city (str).
#     Then print exactly: "My name is <name>, I am <age>, and I live in <city>."
# YOUR CODE HERE
name='Sagar'
age='33'
city='Mumbai'
print(f"My name is {name.title()}, I am {age}, and I live in {city.title()}")

# Q2) You start with a=5 and b=9. Swap them WITHOUT using a third variable.
# YOUR CODE HERE
a = 5 
b = 9
a,b=b,a
print (a == 9)
print (b==5) 


# Q3) You receive x = "120" (string) and y = 30 (int). Create total = 150 as a number.
# YOUR CODE HERE
x=120
y=30
z= x+y
print(f'Total Number is {z}')

# Q4) Given minutes = 135, compute hours and remaining_minutes using integer math.
#     Then print: "2 hours 15 minutes"
# YOUR CODE HERE
Hours = int(120/60)
min = int(0.25*60)
print (f'Time is {Hours} hours {min} minutes')

# ====================== DATA TYPES ======================

# Q5) For each value in the list, print the value and its type: 1, 1.0, True, 1+0j, "1", None
#     (one per line, no extra text)
# YOUR CODE HERE
values = [1, 1.0, 'True', 1+0j, "1", 'None']
type=['Number','float','boolean','complex','string','Nonetype']
for i,t in zip(values,type):
    print (f'{t}= {i}')

# Q6) Convert "101101" from base 2 to an integer; store in n_bin.
# YOUR CODE HERE
n_bin=int("101101",2)
print(n_bin)

# Q7) Given maybe = "42.0": convert to int IF it represents a whole number, else to float.
#     Store the result in num.
# YOUR CODE HERE
maybe = "42.0"
f = float(maybe)                     # parse as float first
num = int(f) if f.is_integer() else f  # int if whole, else keep float
print(num)                    

# Q8) Build a list called truthy_flags with bool() of each from: [0, 1, -2, "", "0", [], [0]]
# YOUR CODE HERE
truthy_flags=  [0, 1, -2, "", "0", [], [0]]
for flags in truthy_flags:
    print(f'{bool(flags)}')


# ====================== STRINGS ======================

# Q9) Given s = "  Hello, Python!  ":
#     - remove surrounding spaces
#     - change to lowercase
#     - replace "python" with "world"
#     Final variable must be s2.
# YOUR CODE HERE
s = "  Hello, Python!  "
s2 = s.strip().lower().replace('python','world')
print(s2)

# Q10) Given s = "abc123xyz456", extract "123xyz" using slicing only (no loops, no finds).
#      Store in part.
# YOUR CODE HERE
s = "abc123xyz456"
s2= s[3:9]
print(s2)

# Q11) Define a function is_pal(s) that returns True if s is a palindrome
#      ignoring case and non-alphanumeric characters.
# YOUR CODE HERE



# Q12) Given full = "Ada Lovelace", produce "Lovelace, Ada" (store in flipped).
# YOUR CODE HERE
full = "Ada Lovelace"
sd = full.split('Ada')
ds = full.split('Lovelace')
print(f'{sd,} {ds}')

# ====================== LISTS ======================

# Q13) nums = [10, 20, 30, 40, 50]. Replace just the middle element(s) so list becomes:
#      [10, 20, 99, 100, 40, 50]
#      (Do not rebuild a new list variable; mutate the existing one.)
# YOUR CODE HERE
nums = [10, 20, 30, 40, 50]
nums[2]=99
nums.insert(3,100)
print(nums)

# Q14) From src = [1,2,3,2,4,2,5], create no_twos that contains all elements except 2.
#      Do NOT use list.remove in a loop.
# YOUR CODE HERE
src = [1,2,3,2,4,2,5]
no_twos = []
for x in src:
    if x != 2:
        no_twos.append(x)
print(no_twos)

# Q15) words = ["apple","Banana","cherry","apricot","banana"].
#      Sort case-insensitively and store in sorted_words (stable ties).
# YOUR CODE HERE
words = ["apple","Banana","cherry","apricot","banana"]
sorted_words=sorted(words)
print(sorted_words)

# Q16) nested = [[1,2],[3,[4,5]],6]. Create a new list flat that contains all numbers
#      at one level (i.e., [1,2,3,4,5,6]) by writing a recursive function flatten().
# YOUR CODE HERE
nested = [[1,2],[3,[4,5]],6]
print(*nested)



# ====================== (Optional) QUICK RUN AREA ======================
# Use this area to manually call your functions or print variables while testing.
# Keep it minimal; don't reveal expected outputs here.

if __name__ == "__main__":
    pass  # You can replace this with small, temporary prints while testing.
