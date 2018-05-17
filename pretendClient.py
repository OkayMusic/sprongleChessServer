import socket

HELP = "POST / HTTP/1.1\r\n\r\nH"

SPRONGLE_LOGIN = "POST / HTTP/1.1\r\n\r\nContent: AppStart\r\nFrom: 1234\r\nName: Sprongle"
CHOPS_LOGIN = "POST / HTTP/1.1\r\n\r\nContent: AppStart\r\nFrom: 4321\r\nName: Dr Chops"
MICHAEL_LOGIN = "POST / HTTP/1.1\r\n\r\nContent: AppStart\r\nFrom: 6969\r\nName: Mr Michael"
MAGNET_LOGIN = "POST / HTTP/1.1\r\n\r\nContent: AppStart\r\nFrom: 1337\r\nName: Magnet Man"


SPRONGLE_LOGOUT = "POST / HTTP/1.1\r\n\r\nContent: AppClose\r\nFrom: 1234\r\nName: Sprongle"
CHOPS_LOGOUT = "POST / HTTP/1.1\r\n\r\nContent: AppClose\r\nFrom: 4321\r\nName: Dr Chops"
MICHAEL_LOGOUT = "POST / HTTP/1.1\r\n\r\nContent: AppClose\r\nFrom: 6969\r\nName: Mr Michael"
MAGNET_LOGOUT = "POST / HTTP/1.1\r\n\r\nContent: AppClose\r\nFrom: 1337\r\nName: Magnet Man"


S_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 1234\r\nTo: 4321\r\nGame: 1"
C_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 4321\r\nTo: 1234\r\nGame: 1"
M_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 6969\r\nTo: 1234\r\nGame: 1"
MICK_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 6969\r\nTo: 1234\r\nGame: 1"
MAG_GAMESTART = "POST / HTTP/1.1\r\n\r\nContent: GameStart\r\nFrom: 1337\r\nTo: 6969\r\nGame: 1"


S_CHESSMOVE = "POST / HTTP/1.1\r\n\r\nContent: ChessMove\r\nFrom: 1234\r\nTo: 4321\r\nGame: 1\r\nMove: c5"
C_CHESSMOVE = "POST / HTTP/1.1\r\n\r\nContent: ChessMove\r\nFrom: 4321\r\nTo: 1234\r\nGame: 1\r\nMove: c5"
MICK_CHESSMOVE = "POST / HTTP/1.1\r\n\r\nContent: ChessMove\r\nFrom: 6969\r\nTo: 1234\r\nGame: 69\r\nMove: c5"
MAG_CHESSMOVE = "POST / HTTP/1.1\r\n\r\nContent: ChessMove\r\nFrom: 1337\r\nTo: 6969\r\nGame: 69\r\nMove: d4"


S_GAMESTATEREQUEST = "POST / HTTP/1.1\r\n\r\nContent: GameStateRequest\r\nFrom: 1234\r\nGame: 1"
C_GAMESTATEREQUEST = "POST / HTTP/1.1\r\n\r\nContent: GameStateRequest\r\nFrom: 4321\r\nGame: 1"
MICK_GAMESTATEREQUEST = "POST / HTTP/1.1\r\n\r\nContent: GameStateRequest\r\nFrom: 6969\r\nGame: 69"
MAG_GAMESTATEREQUEST = "POST / HTTP/1.1\r\n\r\nContent: GameStateRequest\r\nFrom: 1337\r\nGame: 69"


if __name__ == "__main__":
    target_IP = "sprongle.com"
    target_port = 80
    BUFSIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_IP, target_port))

    s.send(MAG_CHESSMOVE)

    data = s.recv(BUFSIZE)
    print data
    s.close()
