# AI Calculator
"""User can type what calculation they need to do"""

while True:
    msg1 = "\nWhat calculation would you like to do? "

    msg11 = ['+', '-', '/', '*', 'add', 'sub', 'multi', 'div', 'division', 'multiplication', 'subtraction', 'addition']

    msg12 = ['done', 'exit', 'quit']

    msg13 = f"\nTo end type = {(" / ".join(msg12))} or Type 'C' to continue: "
    
    msg2 = input(msg1)
    msg21 = msg2.lower()

    # Check whether the input is a valid operator
    if msg21 not in msg11:
        print(f"\nTry again, {msg2} is not a valid operator")

        msg15 = input(msg13).lower()

        if msg15.upper() == 'C':
            print("\nStarting program again")
            continue  
        elif msg15 in msg12:
            print("\nStopping program")
            break
        else:
            print("\nInvalid entry, Stopping program")
            break

    msg3 = (f"\nWhat numbers would you like to {msg21}?")  # Fixed typo
    print(msg3)

    # Check whether the input is a number 
    while True:  # Changed while msg21 to while True to ensure a proper loop structure
        msg4 = "\nFirst number: "
        msg6 = input(msg4)
    
        if not msg6.isdigit():
            print(f"\n{msg6} is not a number. Write a number")
            continue

        while True:  # Changed while msg21 to while True to maintain consistent flow
            msg5 = "\nSecond number: "
            msg7 = input(msg5)
            
            if not msg7.isdigit():
                print(f"\n{msg7} is not a number. Write a number")
                continue
            else:
                break
        
        break  # Break outer loop when both numbers are valid

    # Functions for calculations
    def add(a, b):
        return int(a) + int(b)  # Addition function for two integers

    def subtract(c, d):
        return int(c) - int(d)  # Subtraction function

    def multi(e, f):
        return int(e) * int(f)  # Multiplication function

    def div(g, h):
        if int(h) == 0:
            return "Cannot divide by zero"  # Prevents division by zero errors
        return int(g) / int(h)

    # Improved calculations using a dictionary
    # Why? Using a dictionary avoids long if-elif chains, making the code more readable and scalable.
    # Instead of checking multiple conditions, we can directly map an operation to its corresponding function.
    operations = {
        "+": add, "add": add, "addition": add,
        "-": subtract, "sub": subtract, "subtraction": subtract,
        "*": multi, "multi": multi, "multiplication": multi,
        "/": div, "div": div, "division": div
    }

    # Improved the calculation logic
    # Why? This method makes it easier to maintain and add new operations if needed.
    if msg21 in operations:
        print(f"\nYour result is: {operations[msg21](msg6, msg7)}") 
        # How the Code Runs:
        # The user enters +, so msg21 = "+".
        # The program checks if "+" is in operations (it is).
        # It calls operations["+"](5, 10), which means add(5, 10).
        # The add() function runs:
        

    else:
        print("\nInvalid operator.")
    
    # Exiting or continuing the program
    msg14 = input(msg13).lower()

    if msg14 in msg12:
        print("\nStopping program")
        break
    elif msg14.upper() == 'C':
        print("\nStarting program again")
        continue
    else:
        print("\nInvalid Entry. Stopping program")
        break

    # Summary of improvements:
    # 1. Used while True loops instead of while msg21 to ensure correct flow control.
    # 2. Improved input validation to prevent incorrect data from crashing the program.
    # 3. Used a dictionary for cleaner operation handling instead of long if-elif chains.
    # 4. Added a division by zero check to prevent program crashes.
    # 5. Fixed typos and made error messages clearer.
