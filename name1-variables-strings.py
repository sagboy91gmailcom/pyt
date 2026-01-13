# Variabled and Strings
name= " ada  "
name2=" lovelace "
print(name.title()) #getting names is proper cases using title

print(name.upper()) # upper case

print(name.lower()) # lowercase 

fullname= f"{name}{name2}" # f strings - we can use string variables to print or store when printing.

print(f"\tHello,\n{fullname.title()}") # \t = tab space \n = next line

print(f"hello, {fullname.title().rstrip()}") # remove space from right side

print(f"\tHello,\n{fullname.title().rstrip()}")

print(f"\tHello,\n{fullname.title().lstrip()}") # remove space from left side