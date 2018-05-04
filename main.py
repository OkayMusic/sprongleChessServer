import socket
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
        self.active_player_dict = {}

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
            connection.settimeout(600)
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
                    if split_line[0] == "Content-Type":
                        content_type = split_line[1]

                # payload of the message formatted as a list, if you want to see what
                # this looks like just uncomment the print line below
                payload = data_list[data_list.index("") + 1:]
                # print "*---------PAYLOAD---------*\n", payload
                # print "*-------CONTENT-TYPE-------*\n", content_type

                if content_type == "AppStart":
                    self.handle_AppStart(connection, payload)
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

        # now we have this info, we can add the user to the active player dict.
        # if the user is already in the active player dict, we add this IP to the
        # user's IP_list
        try:
            if user_ID not in self.active_player_dict:
                self.active_player_dict[user_ID] = User(user_ID)
                self.active_player_dict[user_ID].say_hello_to_boi()
                reply = "Successfully said hello to boi"
            else:
                reply = ("This boi was already flagged as active. This "
                         "is probably another of boi's devices. If you "
                         "see this message frequently it is possible "
                         "that boi is not getting said goodbye to properly.")
            connection.send(Server.OK + Server.LEN +
                            str(len(reply)) + "\r\n\r\n" + reply)
        except:
            # the only way this could fail is if POST request was invalid
            reply = "user_ID not provided!"
            connection.send(BAD, )

        print self.active_player_dict

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
            self.active_player_dict[user_ID].say_goodbye_to_boi()
            del self.active_player_dict[user_ID]
            print self.active_player_dict
        except Exception as e:
            print e
            print "You probably tried to disconnect a player who was offline"

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
            self.active_player_dict[user1_ID].record_chess_move(game_ID, move)
            self.active_player_dict[user2_ID].record_chess_move(game_ID, move)
            reply = "Move registered and confirmed as legal."
            connection.send(Server.OK + Server.LEN + str(len(reply)) +
                            "\r\n\r\n" + reply)

        except:
            print "one of the players was offline, log them in and try again"

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

        FEN = self.active_player_dict[user_ID].games[game_ID].fen()
        print "Requested FEN: ", FEN
        connection.send(
            Server.OK + Server.TYPE + "FEN\r\n" + Server.LEN + str(len(FEN)) +
            "\r\n\r\n" + FEN)


if __name__ == "__main__":
    PORT = 1336

    MainServer = Server(PORT)
    MainServer.listen()
