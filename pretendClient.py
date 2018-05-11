import socket

SPRONGLE_LOGIN = "POST / HTTP/1.1\r\n\r\nContent: AppStart\r\nFrom: 1234\r\nName: Sprongle"
CHOPS_LOGIN = "POST / HTTP/1.1\r\n\r\nContent: AppStart\r\nFrom: 4321\r\nName: Dr Chops"

SPRONGLE_LOGOUT = "POST / HTTP/1.1\r\n\r\nContent: AppClose\r\nFrom: 1234\r\nName: Sprongle"
CHOPS_LOGOUT = "POST / HTTP/1.1\r\n\r\nContent: AppClose\r\nFrom: 4321\r\nName: Dr Chops"


S_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 1234\r\nTo: 4321\r\nGame: 1"
C_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 4321\r\nTo: 1234\r\nGame: 1"

S_CHESSMOVE = "POST / HTTP/1.1\r\n\r\nContent: ChessMove\r\nFrom: 1234\r\nTo: 4321\r\nGame: 69\r\nMove: e4"
C_CHESSMOVE = "POST / HTTP/1.1\r\n\r\nContent: ChessMove\r\nFrom: 4321\r\nTo: 1234\r\nGame: 69\r\nMove: e4"

S_GAMESTATEREQUEST = "POST / HTTP/1.1\r\n\r\nContent: GameStateRequest\r\nFrom: 1234\r\nGame: 1"
C_GAMESTATEREQUEST = "POST / HTTP/1.1\r\n\r\nContent: GameStateRequest\r\nFrom: 4321\r\nGame: 1"


if __name__ == "__main__":
    target_IP = "192.168.0.31"
    target_port = 1336
    BUFSIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_IP, target_port))

    # s.send(CHOPS_LOGIN)
    # s.send(SPRONGLE_LOGIN)
    # s.send(C_GAMESTART)
    # s.send(S_CHESSMOVE)
    s.send(C_GAMESTATEREQUEST)
    # s.send(CHOPS_LOGOUT)
    # s.send(SPRONGLE_LOGOUT)

    data = s.recv(BUFSIZE)
    print data
    s.close()
