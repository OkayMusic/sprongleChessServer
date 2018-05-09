import os
import glob
import chess
import errno
import datetime

from chess import Board
from convenience import board_to_game


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

        self.directory = "Data/" + self.player_ID + "/"

        # a dict containing a tuple of user's games and info about the game
        # this cant be a bad use of ram!!!!!
        # dict is indexed by facebook game_ID
        self.games = {}
        self.load_all_games()

    def load_all_games(self):
        """
        Load all of the player's games into RAM. This should be called when the
        player logs in. In the future this should be depracated in favour of a
        less retarded system.
        """
        file_list = glob.glob(self.directory + '*.pgn')

        key_list = []  # we can get the keys from the globbed filenames
        pgn_list = []  # and we can get pgn objects
        for files in file_list:
            open_game = open(files)
            game_ID = files.split('/')[-1].split('.')[0]
            self.games[game_ID] = Board()

            PGN = chess.pgn.read_game(open_game)

            # prepare the board
            ply_counter = 0  # this is fucking dumb, fix this future richard
            for moves in PGN.main_line():
                self.games[game_ID].push(moves)
                ply_counter += 1  # f

            # work out which colour the user is playing as
            for keys in PGN.headers:
                if PGN.headers[keys] == self.player_ID:
                    self.games[game_ID].my_colour = keys

            if (ply_counter % 2 == 0) != (self.games[game_ID].my_colour == "Black"):
                self.games[game_ID].my_turn = True
            else:
                self.games[game_ID].my_turn = False

        print self.games

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

    def record_move(self, game_ID, move):
        """
        Record move in board indexed by game_ID, checking for validity
        """
        try:
            self.games[game_ID].push_san(move)
            self.games[game_ID].my_turn = not self.games[game_ID].my_turn
        except:
            print "Move not legal OR incorrectly formatted OR game not started"

        print "FEN: ", self.games[game_ID].fen()
        # print "Move stack: ", self.games[game_ID][0].move_stack

    def begin_game(self, game_ID, colour):
        """
        Register a new game in self.games
        """
        if game_ID not in self.games:
            self.games[game_ID] = Board()
            self.games[game_ID].my_colour = colour
            self.games[game_ID].my_turn = False
            if colour == "White":
                self.games[game_ID].my_turn = True
        else:
            print "Malfunction. Tried to start a game which already exists."
            return

    def write_to_disk(self):
        print "Writing data for user number", self.player_ID, "to disk"
        fen_games = []
        for keys in self.games:
            game = board_to_game(self.games[keys])

            game.headers["Site"] = "sprongleChess"
            game.headers["Date"] = datetime.datetime.now(
            ).strftime("%y-%m-%d %H:%M")
            game.headers[self.games[keys].my_colour] = self.player_ID
            fen_games.append(game)

            # if the user doesn't already have a folder, make one for them
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)

            with open(self.directory + keys + '.pgn', 'w') as open_file:
                open_file.write(str(game))
            print game
