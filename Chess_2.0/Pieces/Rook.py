from Errors import ImpossibleMoveException, PieceColorException
from util import cord_to_pos, pos_to_cord

from contextlib import suppress



def construct_rooks(board):
    board[0][0] = Rook("white", (0, 0))
    board[0][7] = Rook("white", (7, 0))
    board[7][0] = Rook("black", (0, 7))
    board[7][7] = Rook("black", (7, 7))

    return board


class Rook:
    def __init__(self, color, pos):
        self.pos = pos
        self.old_pos = pos

        self.name = "Rook"
        self.sym = "R"

        self.color = color if color in ("white", "black") else None

    def move(self, board, new_pos):
        print(f"New pos: {new_pos}")
        # if board.board[new_pos[1]][new_pos[0]] != 0:

        pos_change = abs(self.pos[0] - new_pos[0]), abs(self.pos[1] - new_pos[1])

        if (pos_change[0] != 0 and pos_change[1] != 0) or not (8 > new_pos[0] > -1 and 8 > new_pos[1] > -1):
            raise ImpossibleMoveException(self, f"{self.name} can't reach", self.pos, new_pos)
        elif pos_change[0] == 0 and pos_change[1] == 0:
            raise ImpossibleMoveException(self, "Need to move", self.pos, new_pos)

        check = self.piece_blocking_check(board, new_pos, pos_change)
        if check:
            raise ImpossibleMoveException(self, f"Another piece is blocking the way on {pos_to_cord(check)}", self.pos, new_pos)



        # elif board.board[new_pos[1]][new_pos[0]] != 0:
        #     raise ImpossibleMoveException(self, "Another piece is blocking the way", self.pos, new_pos)

        return new_pos

    def piece_blocking_check(self, board, new_pos, pos_change):
        pos_axes = 0 if pos_change[0] != 0 else 1
        mult = -1 if self.pos[pos_axes] - new_pos[pos_axes] > 0 else 1

        for i in range(1, pos_change[pos_axes]):
            if pos_axes == 0:
                if board.board[self.pos[1]][self.pos[0] + (mult * i)] != 0:
                    return self.pos[0] + (mult * i), self.pos[1]
            elif pos_axes == 1:
                if board.board[self.pos[1] + (mult * i)][self.pos[0]] != 0:
                    return self.pos[0], self.pos[1] + (mult * i)
        else:
            return

    def piece_attack_check(self, board, king_pos):
        if board.attacking_pos[self.color].get((self.name, self.old_pos)):
            board.attacking_pos[self.color].pop((self.name, self.old_pos))

        print(board.attacking_pos[self.color])
        try:
            y = int((king_pos[1] - self.pos[1]) / abs(king_pos[1] - self.pos[1]))
        except ZeroDivisionError:
            y = 0

        try:
            x = int((king_pos[0] - self.pos[0]) / abs(king_pos[0] - self.pos[0]))
        except ZeroDivisionError:
            x = 0

        print("CHECK:")
        print(f"Old pos: {self.old_pos}")
        print(f"pos: {self.pos}")
        print(f"king pos: {king_pos}")
        print(x, y)

        board.attacking_pos[self.color][(self.name, self.pos)] = list()
        for i in range(1, 8):
            print("x", self.pos[1], self.pos[0] + (i * x), x)
            print("y", self.pos[1] + (i * y), self.pos[0], y)
            with suppress(IndexError):
                if x in (1, -1):
                    board.attacking_pos[self.color][(self.name, self.pos)].append((self.pos[0] + (i * x), self.pos[1]))
                if y in (1, -1):
                    board.attacking_pos[self.color][(self.name, self.pos)].append((self.pos[0], self.pos[1] + (i * y)))

                if board.board[self.pos[1]][self.pos[0] + (i * x)] != 0:
                    x = 0
                if board.board[self.pos[1] + (i * y)][self.pos[0]] != 0:
                    y = 0

        print(board.attacking_pos[self.color][(self.name, self.pos)])




