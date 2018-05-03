import chess
from chess import Board

class User(object):
    """
    welcome to my user class, please enjoy your stay
    """
    def __init__(self, player_ID):
        """
        Init is called every time someone logs back in, so we're going to throw
        all the user's games back into ram and all that good shit. Chess games
        are very cheap, so this should be fine for a good long while.
        """
        # player's unique sprongleChess ID. One per facebook account
        self.player_ID = player_ID

        # is the player online on any device? could be online on multiple
        self.is_online = False
        # this should be populated whenever we say hello to one of the bois devices
        self.IP_list = []

        self.games =

    def say_hello_to_boi(self, device_IP):
        """
        This should be called whenever a connection is received from a new IP
        address.
        """
        self.is_online = True
        self.IP_list.append(device_IP)

    def say_goodbye_to_boi(self, device_IP):
        """
        This should be called whenever a boi logs closes the game on a specific
        device. By taking the device's IP out of IP_list we make sure we dont
        keep throwing game updates at that device, and then we check to see if
        the dude is offline on all devices, in which case we write all his game
        states to disk and stuff (gone but not forgotten frendly boi).
        """
        self.IP_list.remove(device_IP)
        if self.IP_list == []:
            self.is_online = False
            self.write_to_disc()

    def write_to_disk(self):
        pass
