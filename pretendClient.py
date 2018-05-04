import socket

CHESSMOVE = "POST / HTTP/1.1\r\nContent-Type: ChessMove\r\n\r\nFrom: 1234\r\nTo: 4321\r\nGame: 69\r\nMove: e4"

GAMESTATEREQUEST = "POST / HTTP/1.1\r\nContent-Type: GameStateRequest\r\n\r\nFrom: 1234\r\nGame: 69"

CHOPS_LOGIN = "POST / HTTP/1.1\r\nContent-Type: AppStart\r\n\r\nFrom: 4321\r\nName: Dr Chops"
SPRONGLE_LOGIN = "POST / HTTP/1.1\r\nContent-Type: AppStart\r\n\r\nFrom: 1234\r\nName: Sprongle"


def one_shot_message(socket, target_IP, target_port, message):
    s.connect((target_IP, target_port))
    s.send(message)
    s.close()


if __name__ == "__main__":
    target_IP = "192.168.0.21"
    target_port = 1337
    BUFSIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_IP, target_port))
    # s.send(CHOPS_LOGIN)
    # s.send(SPRONGLE_LOGIN)
    # s.send(CHESSMOVE)
    s.send(GAMESTATEREQUEST)
    data = s.recv(BUFSIZE)
    print data
    s.close()
