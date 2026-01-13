class Dog: # a simple class
    """A simple attempt to model a dog"""
    def __init__(self,name,age):
        """Initialize name and age attributes"""
        self.name = name
        self.age=age

    def sit(self):
        """simulate a sittingin repsonse to a command"""    
        print(f"{self.name} is now sitting")

    def roll_over(self):
        """simultate rolling over in response to a command"""    
        print(f"{self.name} rolled over!")

#Making a instance from a class
my_dog = Dog('Wille',6)

print (f"my dog's name is {my_dog.name}.")
print(f"My dog is {my_dog.age} years old.")

#Accessing the attributes
my_dog.name

#calling methods
my_dog.sit()
my_dog.roll_over()