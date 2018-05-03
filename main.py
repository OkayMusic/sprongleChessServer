import socket
from user import User

PORT_NUMBER = 1337

if __name__ == "__main__":
    ServerSocket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_STREAM)
    ServerSocket.bind(('', PORT_NUMBER))

    # max backlog size of 5
    ServerSocket.listen(5)

    # store all active connections (users) here
    # key = fb ID,
    active_player_dict = {}

    while True:
        connection, addr = ServerSocket.accept()
        connection_list.append()
        try:
            data = connection.recv(1024)
        except:
            # maybe doing something here would be a good idea
            pass
