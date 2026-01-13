class Restaurant:

    def __init__(self,rest_name,cusi_type):

        self.rest_name=rest_name
        self.cusi_type=cusi_type

    def describe_rest(self):
        print(f"This is the restaurant name {self.rest_name}")
        print(f"This is the cusine {self.cusi_type} served here\n")

rest = Restaurant('Viceroy','bar-chinese')
print(rest.cusi_type)
print(rest.rest_name,'\n')

rest.describe_rest()



rest1 = Restaurant('bindya','dancebar')
rest1.describe_rest()

rest2=Restaurant('vice1','drinks')
rest2.describe_rest()


