import numpy as np

class User(object):
    def __init__(self):
        # player's unique sprongleChess ID. One per facebook account
        self.ID = 0

        # is the player online on any device? could be online on multiple
        self.is_online = False
        # this should be populated whenever we say hello to one of the bois devices
        self.IP_list = []

    def say_hello_to_boi(self):
        self.is_online = True

    def say_goodbye_to_boi(self, device_IP):
        self.is_online = False
        self.write_to_disc()

    def write_to_disc(self):
        pass
