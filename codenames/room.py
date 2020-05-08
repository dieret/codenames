from codenames.users import Users
from codenames.messages import Messages, Message
from codenames.playground import Playground


class Room(object):
    def __init__(self, number):
        self.number = number
        self.restart()

    def restart(self):
        if self.number <= 4:
            filename = "words.txt"
        else:
            filename = "words_en.txt"
        self.playground = Playground.generate_new(filename=filename)
        self.users = Users()
        self.messages = Messages()
        self.messages.add_message(Message("You are in room {number}".format(number = self.number+1)))
