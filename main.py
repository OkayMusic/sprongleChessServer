import socket
import random
import threading
import thread
from user import User


class MyDict(dict):
    """
    Inherit from MyDict if you want the dict to be printed whenever __setitem__
    or __delitem__ are called.
    """

    def __setitem__(self, key, value):
        super(MyDict, self).__setitem__(key, value)
        self.print_dict()

    def __delitem__(self, key):
        super(MyDict, self).__delitem__(key)
        self.print_dict()

    def print_dict(self):
        printstr = '{'
        for items in self:
            printstr += "'" + items + "': " + str(self[items]) + ', '

        if self:
            printstr = printstr[:-2]  # remove trailing comma if dict not empty

        print printstr + '}'


class Server(object):
    """
    welcome to my server class, please enjoy your stay
    """
    OK = "HTTP/1.1 200 OK\r\n"
    BAD = "HTTP/1.1 400 Bad Request\r\n"
    LEN = "Content-Length: "
    TYPE = "Content-Type: "
    ACCESS = "Access-Control-Allow-Origin: *\r\n"

    def __init__(self, port, is_threading):
        """
        Initializes the server on the specified port
        """
        print "Initializing server..."
        self.port = port
        self.is_threading = is_threading
        self.sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))

        # the managed attribute _active users. See the property for more info
        self.active_users = MyDict({})

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
            if self.is_threading:
                threading.Thread(target=self.listen_to_boi,
                                 args=(connection, addr)).start()
            # running without threading is useful for debugging purposes
            else:
                self.listen_to_boi(connection, addr)

    def listen_to_boi(self, connection, addr):
        """
        This is where we get the connection from the client, work out what type
        of message we were sent and shoot off the message to the appropriate
        handler.
        """
        print "Connection accepted to", addr[0], "on port", addr[1]
        bufsize = 2048
        while True:
            try:
                data = connection.recv(bufsize)

                # some protocols make the server close the connection
                # they do this by sending an empty message
                # so before trying to parse, we check for an empty message
                if data.split() == []:
                    print "Closing connection to", addr[0], "on port", addr[1]
                    print '\n'
                    connection.close()
                    return  # end thread execution here

                print "*----------------DATA----------------*\n", data
                print "*------------------------------------*"

                # useful boi for parsing
                data_list = [x.split(': ') for x in data.split("\r\n")]
                # grab the payload; what we do with the payload depends on the
                # content type
                payload = data_list[(data_list.index([""]) + 1):]

                # parse whatever we were sent to find the content type
                content_type = ""
                for lines in data_list:
                    if lines[0] == "Content":
                        content_type = lines[1]

                # check to see whether or not the user is sending a help request
                if payload[0][0].lower() == "help" or \
                        payload[0][0].lower() == "h":
                    content_type = "Help"
                if content_type[-4:] == "Help":
                    self.handle_Help(connection, content_type)
                    return

                try:
                    getattr(self, "handle_" + content_type)(connection, payload)
                except:
                    reply = "Invalid Content header"
                    self.send_message(connection, reply, success=False)
            except:
                print "Closing connection.\n\n"
                connection.close()
                return  # end thread execution here

    def handle_Help(self, connection, content_type):
        """
        Called whenever we receive any Help POST request.

        Required header field:

        'Help'
        OR
        'Content: Help'
        OR
        'Content: <ContentType>Help'

        Any additional header fields will be ignored, but will not cause errors
        if sent.

        On success, if the message was just 'Content: Help' then a list of
        acceptable content headers will be sent. If the request was of the form
        'Content: <ContentType>Help' then the docstring for the ContentType's
        request handler will be sent.
        """
        print 1
        if content_type == "Help":
            reply = ("\r\nAll messages to the server should take the form:\r\n\r\n"
                     "Content: <ContentType>\r\n"
                     "MoreHeaders: <MoreValues>\r\n...\r\n\r\n"
                     "Where at least as many additional headers and values \r\n"
                     "are given as are required by the content type handler.\r\n"
                     "Currently accepted Content types:\r\n\r\n")
            for attr in dir(self):
                if attr[:6] == "handle":
                    if attr[7:] == "Help":
                        reply += "'" + attr[7:] + "'\r\n"
                    else:
                        reply += "'" + attr[7:] + \
                            "', '" + attr[7:] + "Help'\r\n"

            reply += ("\r\nIn order to find out what additional header and\r\n"
                      "value fields you should supply in order to send a valid\r\n"
                      "ContentType request, send the server a:\r\n"
                      "'Content: <ContentType>Help'\r\n"
                      "message. This will give you more info on how to use the\r\n"
                      "ContentType request, and let you know what kind of\r\n"
                      "response you should expect\r\n")
            self.send_message(connection, reply, success=True)
        else:
            reply = getattr(self, "handle_" +
                            content_type[:-4]).__doc__
            self.send_message(connection, reply, success=True)

    def handle_AppStart(self, connection, payload):
        """
        Called whenever we receive an AppStart POST request.

        Required header field:

        'From: <FB_user_ID>'.

        Any additional data should be sent in the format 'DataType: Data', and
        will be automatically stored by the server. Header fields should be
        separated by carriage returns.

        Returns a success message on success, failed message on fail.
        """
        headers = ["From"]

        [user_ID], excess = self.parse_payload(
            connection, payload, headers)

        # now we have this info, we can add the user to the active user dict.
        # if the user is already in the active user dict, we add this IP to the
        # user's IP_list
        try:
            if user_ID not in self.active_users:
                self.active_users[user_ID] = User(user_ID)

                reply = "Successfully said hello to boi"
            else:
                reply = ("This boi was already flagged as active. This "
                         "is probably another of boi's devices. If you "
                         "see this message frequently it is possible "
                         "that boi is not getting said goodbye to properly.")
            self.send_message(connection, reply, success=True)
        except:
            # not sure how this could fail, but regardless it should be handled
            reply = "Failed to log in user."
            self.send_message(connection, reply, success=False)

    def handle_AppClose(self, connection, payload):
        """
        Called whenever we receive an AppClose POST request.

        Required header field:

        'From: <FB_user_ID>'.

        Any additional header fields will be ignored, but will not cause errors
        if sent.

        Returns a success message on success, failed message on fail. On
        success, all user data and game data is written to disk.
        WARNING: data could be lost if users are not logged out properly.
        """
        headers = ["From"]
        [user_ID], excess = self.parse_payload(connection, payload, headers)

        try:
            self.active_users[user_ID].say_goodbye_to_boi()
            del self.active_users[user_ID]
            reply = ("Successfully said goodbye to boi, and wrote all his data "
                     "to disk.")
            self.send_message(connection, reply, success=True)
        except:
            reply = ("AppClose failed on the serverside, data could be lost. "
                     "Are you sure that you didn't try to disconnect a user"
                     " who is already offline?")
            self.send_message(connection, reply, success=False)

    def handle_ChessMove(self, connection, payload):
        """
        Called whenever we receive a ChessMove POST request.

        Required header fields:

        'From: <FB_user_ID>' # user_ID of player sending the message
        'To: <FB_user_ID>' # user_ID of opponent
        'Game: <FB_game_ID>' # FB generated ID of the game in play
        'Move: <SAN chess move>' # this is checked for legality by the server

        Any additional header fields will be ignored, but will not cause errors
        if sent.

        Returns confirmation that the move was legal on success, on failure the
        reason for failure is sent (but could still contain bugs or misleading
        messages, more testing needed).
        """
        headers = ["From", "To", "Game", "Move"]
        [user1_ID, user2_ID, game_ID, move], excess = self.parse_payload(
            connection, payload, headers)

        try:
            # make sure it is actually user1's turn to move!
            if self.active_users[user1_ID]._games[game_ID].my_turn:
                self.active_users[user1_ID].record_move(game_ID, move)

                # user2 could be offline, if so log him in and record move
                if user2_ID not in self.active_users:
                    self.active_users[user2_ID] = User(user_ID=user2_ID)
                    self.active_users[user2_ID].record_move(game_ID, move)
                    self.active_users[user2_ID].write_games()
                    del self.active_users[user2_ID]
                else:
                    self.active_users[user2_ID].record_move(game_ID, move)
                reply = "Move registered and confirmed as legal."
                self.send_message(connection, reply, success=True)
            else:
                reply = "It isn't your turn to move my friend."
                self.send_message(connection, reply, success=False)

        except:
            reply = ("Failed chessmove. Was the game started via a GameStart "
                     "request?")
            self.send_message(connection, reply, success=False)

    def handle_GameStart(self, connection, payload):
        """
        Called whenever we receieve a GameStart POST request. This request
        should be sent only by the match instigator.

        Required header fields:

        'From: <FB_user_ID>' # user_ID of player sending the message
        'To: <FB_user_ID>' # user_ID of opponent
        'Game: <FB_game_ID>' # FB generated ID of the game in play

        Any additional header fields will be ignored, but will not cause errors
        if sent.

        Returns confirmation that the game was started successfully on success,
        as well as the colour that the instigator will be using. On failure
        a failed message will be sent.
        """
        headers = ["From", "To", "Game"]

        [user1_ID, user2_ID, game_ID], excess = self.parse_payload(
            connection, payload, headers)

        # make sure that the game doesn't already exist
        if game_ID in self.active_users[user1_ID]._games:
            reply = "Failed to start game. Does the game already exist?"
            self.send_message(connection, reply, success=False)
            return

        # pick colours
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
                self.active_users[user2_ID].write_games()
                del self.active_users[user2_ID]
            else:
                self.active_users[user2_ID].begin_game(game_ID, user2_colour)

            reply = "Colour: " + user1_colour + "\r\nGame successfully started."
            self.send_message(connection, reply, success=True)
        except:
            reply = "Failed to start game. Does the game already exist?"
            self.send_message(connection, reply, success=False)

    def handle_GameStateRequest(self, connection,  payload):
        """
        Called whenever we receieve a GameStateRequest POST request.

        Required header fields:

        'From: <FB_user_ID>' # user_ID of player sending the message
        'Game: <FB_game_ID>' # FB generated ID of the game in play

        Any additional header fields will be ignored, but will not cause errors
        if sent.

        On success, returns the current FEN, the user's colour and whether or
        not it is the user's turn to move in the format:

        'FEN: <FEN>'
        'Colour: <user's colour>'
        'IsYourMove: <True/False>'

        On failure, a failed message will be sent.
        """
        # the headers we require for a valid GameStateRequest
        headers = ["From", "Game"]

        [user_ID, game_ID], excess = self.parse_payload(
            connection, payload, headers)

        try:
            reply = self.active_users[user_ID].get_gamestate(game_ID)
            self.send_message(connection, reply, success=True)
        except:
            reply = "Unable to retrieve game state. Does the game exist?"
            self.send_message(connection, reply, success=False)

    def parse_payload(self, connection, payload, headers):
        """
        Parse the payload of an HTTPRequest looking for our required custom
        header fields and their corresponding field values. Returns an ordered
        list of field values such that headers[i]'s field value is value[i].

        If some header fields are included which were not expected (or
        explicitly required) then excess is created. Excess is a dict of the
        excess header fields and field values.
        """
        values = [None for x in range(len(headers))]

        # check for excess headers + make sure we actually have enough headers
        if len(headers) < len(payload):
            excess = {}
        elif len(headers) == len(payload):
            excess = None
        else:
            reply = "Invalid request, not enough headers receieved."
            self.send_message(connection, reply, success=False)
            self.kill_thead(connection)

        for lines in payload:
            if lines[0] in headers:
                values[headers.index(lines[0])] = lines[1]
            else:
                excess[lines[0]] = lines[1]
        return values, excess

    def send_message(self, connection, reply, success=True):
        """
        Sends the 200 OK request, along with the access control headers. Later this
        should handle more bois than 200 OK.
        """

        if success:
            reply = "success\r\n" + reply
        else:
            reply = "failed\r\n" + reply
        print reply

        connection.send(Server.OK + Server.ACCESS + Server.LEN + str(len(reply)) +
                        "\r\n\r\n" + reply)

    def kill_thead(self, connection):
        """
        This should only be called in the event of things going badly wrong.
        Some bad memes can happen to memory by calling thread.exit(), but it is
        better than the thread staying up forever and closing the connection is
        important.
        """
        print "Shit went wrong, had to force kill a thread."
        connection.close()
        thread.exit()


if __name__ == "__main__":
    PORT = 80
    THREADING = True

    MainServer = Server(PORT, THREADING)
    MainServer.listen()
