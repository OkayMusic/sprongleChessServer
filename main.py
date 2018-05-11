import socket
import random
import threading
from user import User


class Server(object):
    """
    welcome to my server class, please enjoy your stay
    """
    OK = "HTTP/1.1 200 OK\r\n"
    BAD = "HTTP/1.1 400 Bad Request\r\n"
    LEN = "Content-Length: "
    TYPE = "Content-Type: "
    ACCESS = "Access-Control-Allow-Origin: *\r\n"

    def __init__(self, port):
        """
        Initializes the server on the specified port
        """
        print "Initializing server..."
        self.port = port
        self.sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))

        # store all active connections (users) here, key = fb ID
        self.active_users = {}

    def send_message(connection, reply, success=True):
        """
        Sends the 200 OK request, along with the access control headers. Later this
        should handle more bois than 200 OK.
        """

        if success:
            reply = "success\r\n" + reply
        else:
            reply = "failed\r\n" + reply

        connection.send(Server.OK + Server.ACCESS + Server.LEN + str(len(reply)) +
                        "\r\n\r\n" + reply)

    def listen(self):
        """
        Listen for any connection. Once a connection is made, a new thread is
        spawned and the tcp connection is maintained until terminated by the
        server via timeout/termination request or until terminated by the
        client.
        """
        self.sock.listen(5)
        print "Server listening on port", self.port, "\n"
        while True:
            connection, addr = self.sock.accept()
            connection.settimeout(5)  # time out connection after 5 secs
            threading.Thread(target=self.listen_to_boi,
                             args=(connection, addr)).start()

    def listen_to_boi(self, connection, addr):
        """
        This is where the individual client-server interactions take place.
        """

        print "Connection accepted to", addr[0], "on port", addr[1]
        bufsize = 1024
        while True:
            try:
                data = connection.recv(bufsize)

                # some protocols make the server close the connection
                # they do this by sending an empty message
                # so before trying to parse, we check for an empty message
                if data.split() == []:
                    print "Closing connection."
                    connection.close()
                    return  # end thread execution here

                print "*----------------DATA----------------*\n", data

                content_type = ""
                data_list = data.split("\r\n")  # useful boi for parsing
                # parse whatever we were sent to find the content type of the data
                for lines in data_list:
                    split_line = lines.split(": ")
                    if split_line[0] == "Content":
                        content_type = split_line[1]

                # payload of the message formatted as a list, if you want to see what
                # this looks like just uncomment the print line below
                payload = data_list[data_list.index("") + 1:]
                # print "*---------PAYLOAD---------*\n", payload
                # print "*-------CONTENT-TYPE-------*\n", content_type

                if content_type == "AppStart":
                    self.handle_AppStart(connection, payload)
                elif content_type == "GameStart":
                    self.handle_GameStart(connection, payload)
                elif content_type == "ChessMove":
                    self.handle_ChessMove(connection, payload)
                elif content_type == "GameStateRequest":
                    self.handle_GameStateRequest(connection, payload)
                elif content_type == "AppClose":
                    self.handle_AppClose(connection, payload)
            except:
                print "Closing connection."
                connection.close()
                return  # end thread execution here

    def handle_AppStart(self, connection, payload):
        """
        Called whenever we receive an AppStart POST request.
        """
        user_ID = ""
        user_name = ""
        for lines in payload:
            lines = lines.split(": ")

            if lines[0] == "From":
                user_ID = lines[1]
            if lines[0] == "Name":
                user_name = lines[1]

        # now we have this info, we can add the user to the active user dict.
        # if the user is already in the active user dict, we add this IP to the
        # user's IP_list
        try:
            if user_ID not in self.active_users:
                self.active_users[user_ID] = User(user_ID)
                self.active_users[user_ID].say_hello_to_boi()
                reply = "success\r\nSuccessfully said hello to boi"
            else:
                reply = ("success\r\nThis boi was already flagged as active. This "
                         "is probably another of boi's devices. If you "
                         "see this message frequently it is possible "
                         "that boi is not getting said goodbye to properly.")
            self.send_message(connection, reply, success=True)
        except:
            # the only way this could fail is if POST request was invalid
            reply = "failed\r\nuser_ID not provided!"
            self.send_message(connection, reply, success=False)

        print self.active_users

    def handle_AppClose(self, connection, payload):
        """
        Called whenever we receive an AppClose POST request.
        """
        user_ID = ""
        for lines in payload:
            lines = lines.split(": ")

            if lines[0] == "From":
                user_ID = lines[1]
        try:
            self.active_users[user_ID].say_goodbye_to_boi()
            del self.active_users[user_ID]
            print self.active_users
            reply = ("success\r\nSuccessfully said goodbye to boi, and wrote all his data "
                     "to disk.")
            self.send_message(connection, reply, success=True)
        except Exception as e:
            print e
            print "You probably tried to disconnect a user who was offline"
            reply = ("failed\r\n AppClose on the serverside, data could be lost. "
                     "Are you sure that you didn't try to disconnect a user"
                     " who is already offline?")
            self.send_message(connection, reply, success=False)

    def handle_ChessMove(self, connection, payload):
        """
        Called whenever we receive a ChessMove POST request.
        """
        user1_ID = ""
        user2_ID = ""
        game_ID = ""
        move = ""
        for lines in payload:
            lines = lines.split(': ')

            if lines[0] == "From":
                user1_ID = lines[1]
            elif lines[0] == "To":
                user2_ID = lines[1]
            elif lines[0] == "Game":
                game_ID = lines[1]
            elif lines[0] == "Move":
                move = lines[1]

        try:
            # make sure it is actually user1's turn to move!
            if self.active_users[user1_ID].games[game_ID].my_turn:
                self.active_users[user1_ID].record_move(game_ID, move)

                # user2 could be offline, if so log him in and record move
                if user2_ID not in self.active_users:
                    self.active_users[user2_ID] = User(user_ID=user2_ID)
                    self.active_users[user2_ID].record_move(game_ID, move)
                    self.active_users[user2_ID].write_to_disk()
                    del self.active_users[user2_ID]
                else:
                    self.active_users[user2_ID].record_move(game_ID, move)

                reply = "success\r\nMove registered and confirmed as legal."
            else:
                reply = "success\r\nIt isn't your turn to move my friend."
            self.send_message(connection, reply, success=True)

        except:
            reply = ("failed\r\n chessmove. Was the game started via a GameStart "
                     "request?")
            print "one of the users was offline, log them in and try again"
            self.send_message(connection, reply, success=False)

    def handle_GameStart(self, connection, payload):
        """
        Called whenever we receieve a GameStart POST request. This request
        should be sent by the match instigator, and the instigator will
        receive in response to their request an OK message as well as
        confirmation of which user will be using which colour.
        """
        user1_ID = ""
        user2_ID = ""
        user1_colour = ""
        user2_colour = ""
        game_ID = ""

        for lines in payload:
            lines = lines.split(': ')

            if lines[0] == "From":
                user1_ID = lines[1]
            elif lines[0] == "To":
                user2_ID = lines[1]
            elif lines[0] == "Game":
                game_ID = lines[1]

        if random.random() < 0.5:
            user1_colour = "Black"
            user2_colour = "White"
        else:
            user1_colour = "White"
            user2_colour = "Black"

        try:
            self.active_users[user1_ID].begin_game(game_ID, user1_colour)

            # user 1 is guaranteed to be online (he just sent the request)
            # user 2, however, could be offline or a first time user
            # we should handle the likely case that user2 is offline!
            if user2_ID not in self.active_users:
                self.active_users[user2_ID] = User(user_ID=user2_ID)
                self.active_users[user2_ID].begin_game(game_ID, user2_colour)
                self.active_users[user2_ID].write_to_disk()
                del self.active_users[user2_ID]
            else:
                self.active_users[user2_ID].begin_game(game_ID, user2_colour)

            reply = "success\r\nColour: " + user1_colour + "\nGame successfully started."
            self.send_message(connection, reply, success=True)
        except:
            print "failed\r\n to start game."
            reply = "failed\r\n to start game. Does the game already exist?"
            self.send_message(connection, reply, success=False)

    def handle_GameStateRequest(self, connection,  payload):
        """
        Called whenever we receive a GameStateRequest POST request.
        """
        user_ID = ""
        game_ID = ""

        for lines in payload:
            lines = lines.split(': ')

            if lines[0] == "From":
                user_ID = lines[1]
            elif lines[0] == "Game":
                game_ID = lines[1]

        try:
            FEN = self.active_users[user_ID].games[game_ID].fen()
            print "Requested FEN: ", FEN
            colour = self.active_users[user_ID].games[game_ID].my_colour
            reply = "success\r\nFEN: " + FEN + "\r\nColour: " + colour
            self.send_message(connection, reply, success=True)
        except:
            reply = "failed\r\n to retrieve game state. Does the game exist?"
            self.send_message(connection, reply, success=False)


if __name__ == "__main__":
    PORT = 1336

    MainServer = Server(PORT)
    MainServer.listen()
