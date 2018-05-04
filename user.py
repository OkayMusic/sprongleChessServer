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
        self.name = ""  # player's irl name mmmmmmmmdata
        #----- more precious user data can go here -----#

        # is the player online on any device? could be online on multiple
        self.is_online = False

        # a dict containing all the games the user has ever played
        # this cant be a bad use of ram!!!!!
        # dict is indexed by facebook game_ID
        self.games = {}

    def say_hello_to_boi(self):
        """
        Set player to be online and load in their chess games.
        """
        self.is_online = True

    def say_goodbye_to_boi(self):
        """
        Better write his precious user data to disk. Also sets the user to be
        offline.
        """
        self.is_online = False
        self.write_to_disk()

    def record_chess_move(self, game_ID, move):
        if game_ID not in self.games:  # if the game hasn't started yet
            self.games[game_ID] = Board()  # loads starting position

        try:
            self.games[game_ID].push_san(move)
        except:
            print "Move not legal OR incorrectly formatted"

        print "FEN: ", self.games[game_ID].fen()
        # print "Move stack: ", self.games[game_ID].move_stack

    def write_to_disk(self):
        print "Writing data for user number", self.player_ID, "to disk"
