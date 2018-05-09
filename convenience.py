import chess
import chess.pgn
import collections

"""
A bunch of possibly unrelated convenience functions. Some day these will be
more well organized, but today is not that day.
"""


def board_to_game(board):
    """
    Takes an abstract chess board object, and returns a pgn Game object.
    """
    game = chess.pgn.Game()

    # Undo all moves.
    switchyard = collections.deque()
    while board.move_stack:
        switchyard.append(board.pop())

    game.setup(board)
    node = game

    # Replay all moves.
    while switchyard:
        move = switchyard.pop()
        node = node.add_variation(move)
        board.push(move)

    game.headers["Result"] = board.result()
    return game
