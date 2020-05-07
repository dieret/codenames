from codenames.users import Users
from codenames.messages import Messages
from codenames.playground import Playground

class Room(object):
    def __init__(self, number):
        self.restart()
        self.number = number

    def restart(self):
        self.playground = Playground.generate_new()
        self.users = Users()
        self.messages = Messages()


    
