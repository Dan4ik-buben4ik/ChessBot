from Errors import ImpossibleMoveException, PieceColorException
from util import cord_to_pos, pos_to_cord

from itertools import chain


def construct_kings(board):
    board[0][3] = King("white", (3, 0))
    board[7][3] = King("black", (3, 7))

    return board


class King:
    def __init__(self, color, pos):
        self.pos = pos
        self.old_pos = pos

        self.name = "King"
        self.sym = "K"

        self.color = color if color in ("white", "black") else None

    def move(self, board, new_pos):
        print(f"New pos: {new_pos}")
        # if board.board[new_pos[1]][new_pos[0]] != 0:

        pos_change = abs(self.pos[0] - new_pos[0]), abs(self.pos[1] - new_pos[1])

        if pos_change[0] not in (0, 1) or pos_change[1] not in (0, 1):
            raise ImpossibleMoveException(self, f"{self.name} can't reach", self.pos, new_pos)
        elif pos_change[0] == 0 and pos_change[1] == 0:
            raise ImpossibleMoveException(self, "Need to move", self.pos, new_pos)

        check = self.check_if_can_go(board, new_pos)
        if check:
            raise ImpossibleMoveException(self, f"Can't go on attacked space", self.pos, new_pos)

        board.kings_pos[0 if self.color == "white" else 1] = new_pos
        return new_pos

    def check_if_can_go(self, board, new_pos):
        # print("DICT: ", board.attacking_pos)
        # print("DICT COLOR: ", board.attacking_pos["white" if self.color == "black" else "black"])
        # print("DICT COLOR VALUE: ", list(chain.from_iterable(board.attacking_pos["white" if self.color == "black" else "black"].values())))
        if new_pos in chain.from_iterable(board.attacking_pos["white" if self.color == "black" else "black"].values()):
            return True
        return

    def piece_attack_check(self, board, king_pos):
        if board.attacking_pos[self.color].get((self.name, self.old_pos)):
            board.attacking_pos[self.color].pop((self.name, self.old_pos))

        try:
            y = int((king_pos[1] - self.old_pos[1]) / abs(king_pos[1] - self.pos[1]))
        except ZeroDivisionError:
            y = 0

        try:
            x = int((king_pos[0] - self.pos[0]) / abs(king_pos[0] - self.pos[0]))
        except ZeroDivisionError:
            x = 0

        board.attacking_pos[self.color][(self.name, self.pos)] = [(self.pos[1] + y, self.pos[0] + x)]


