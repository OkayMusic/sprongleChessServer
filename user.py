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
    _data_file = "user_data.txt"

    def __init__(self, user_ID):
        """
        Init is called every time someone logs back in, so we're going to throw
        all the user's info back into RAM. Note: some User properties are
        defined with a leading underscore. These are attributes that we dont
        want to automatically write to disk using write_data.
        """
        # user's unique sprongleChess ID. One per facebook account
        self.user_ID = user_ID

        # the directory in which the user's data will be stored
        self._directory = "Data/" + self.user_ID + "/"
        # make the directory, if it doesn't already exist
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

        # a dict containing the user's games, indexed by game ID
        self._games = {}

        # load the user's previous games into RAM, alongside previously
        # collected data
        self.load_games()
        self.load_data()

    def record_move(self, game_ID, move):
        """
        Record move in board indexed by game_ID, checking for validity.
        """
        try:
            self._games[game_ID].push_san(move)
            self._games[game_ID].my_turn = not self._games[game_ID].my_turn
            # writes game of player to disk after each legal move
            # this is great for persistence, but a little clunky.
            self.write_game(game_ID)

            return True
        except:
            return False

    def begin_game(self, game_ID, colour):
        """
        Register a new game in self.games
        """
        self._games[game_ID] = Board()
        self._games[game_ID].my_colour = colour
        if colour == "White":
            self._games[game_ID].my_turn = True
        else:
            self._games[game_ID].my_turn = False

    def get_gamestate(self, game_ID):
        fen = self._games[game_ID].fen()
        colour = self._games[game_ID].my_colour
        turn = str(self._games[game_ID].my_turn)
        threefold = str(self._games[game_ID].can_claim_threefold_repetition())
        fivefold = str(self._games[game_ID].is_fivefold_repetition())

        return ("FEN: " + fen + "\r\nColour: " + colour + "\r\nIsYourMove: " +
                turn + "\r\nThreeFold: " + threefold + "\r\nFiveFold: " +
                fivefold)

    def load_games(self):
        """
        Load all of the user's games into self._games
        """
        file_list = glob.glob(self._directory + '*.pgn')

        for files in file_list:
            open_game = open(files)
            game_ID = files.split('/')[-1].split('.')[0]
            self._games[game_ID] = Board()

            PGN = chess.pgn.read_game(open_game)

            # prepare the board
            for moves in PGN.main_line():
                self._games[game_ID].push(moves)

            # work out which colour the user is playing as
            for keys in PGN.headers:
                if PGN.headers[keys] == self.user_ID:
                    self._games[game_ID].my_colour = keys

            if (len(list(PGN.main_line())) % 2 == 0) != \
                    (self._games[game_ID].my_colour == "Black"):
                self._games[game_ID].my_turn = True
            else:
                self._games[game_ID].my_turn = False

    def write_game(self, game_ID):
        """
        Writes a specific game to disk.
        """
        # for debugging purposes, it is useful to print the boards as we go
        print "\nWriting user " + self.user_ID + "'s game with ID " + \
            game_ID + " to disk, the following board position written: \n"
        print self._games[game_ID]
        game = board_to_game(self._games[game_ID])

        game.headers["Site"] = "sprongleChess"
        game.headers["Date"] = datetime.datetime.now(
        ).strftime("%y-%m-%d %H:%M")
        game.headers[self._games[game_ID].my_colour] = self.user_ID

        with open(self._directory + game_ID + '.pgn', 'w') as open_file:
            open_file.write(str(game))

    def write_games(self):
        """
        Writes all of the player's games to disk. Called on logout.
        """
        print "Writing games of user number", self.user_ID, "to disk"
        for keys in self._games:
            self.write_game(keys)

    def load_data(self):
        """
        Load all previously collected data on the user into RAM.
        """
        with open(self._directory + User._data_file, 'w+') as in_file:
            for lines in in_file:
                lines = lines.strip().split(': ')
                setattr(lines[0], lines[1])

    def dict_to_data(self, data_dict):
        """
        Parse a dict with keys = data type, value = data value, and give the
        user the relevant attributes.
        """
        for keys in data_dict:
            setattr(self, keys, data_dict[keys])

    def write_data(self):
        """
        Write all of the User attributes, which dont begin with a leading
        underscore, to disk.
        """
        data = [x for x in dir(self) if not x.startswith('_')
                and not callable(getattr(self, x))]

        with open(self._directory + User._data_file, 'w') as open_file:
            for attrs in data:
                open_file.write(attrs + ': ' + getattr(self, attrs) + '\n')

    def say_goodbye_to_boi(self):
        """
        Write the player's games and data to disk.
        """
        self.write_games()
        self.write_data()
