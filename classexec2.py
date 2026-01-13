class User:

    def __init__(self, firname,secname,age,job):
        self.firname = firname
        self.secname= secname
        self.age= age
        self.job = job

    def desc_user(self):
        print(f"""This is {self.firname} {self.secname}.\
              Age is {self.age} and Occupation is {self.job}""")

    def gree_user(self):
        print(f"welcome {self.firname}{self.secname}")



user1 = User('dhawal',' shah',26,'QA')
user1.gree_user()
user1.desc_user()

