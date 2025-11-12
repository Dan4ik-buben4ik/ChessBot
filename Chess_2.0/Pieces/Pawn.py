from Errors import ImpossibleMoveException, PieceColorException
from util import cord_to_pos


def construct_pawns(board):
    board[1] = list([Pawn("white", (pos_x, 1)) for pos_x in range(8)])
    board[6] = list([Pawn("black", (pos_x, 6)) for pos_x in range(8)])

    return board


class Pawn:
    def __init__(self, color, pos):
        self.pos = pos

        self.name = "Pawn"
        self.sym = "P"

        self.color = color if color in ("white", "black") else None

    def move(self, board, new_pos):
        print(f"New pos: {new_pos}")
        if board.board[new_pos[1]][new_pos[0]] != 0:
            return self.capture(new_pos)

        pos_change = abs(self.pos[0] - new_pos[0]), abs(self.pos[1] - new_pos[1])

        if pos_change[1] not in (1, 2):
            raise ImpossibleMoveException(self, f"{self.name} can't reach", self.pos, new_pos)
        elif pos_change[1] == 0:
            raise ImpossibleMoveException(self, "Need to move", self.pos, new_pos)
        elif pos_change == 2 and not ((self.pos[1] == 1 and self.color == "white") or (self.pos[1] == 6 and self.color == "black")):
            raise ImpossibleMoveException(self, "Pawn can't do a double move", self.pos, new_pos)
        elif (self.pos[1] < new_pos[1] and self.color == "black") or (self.pos[1] > new_pos[1] and self.color == "white"):
            raise ImpossibleMoveException(self, "Pawn can't go back", self.pos, new_pos)
        elif pos_change[0] != 0:
            raise ImpossibleMoveException(self, "Pawn can't move across", self.pos, new_pos)
        # elif board.board[new_pos[1]][new_pos[0]] != 0:
        #     raise ImpossibleMoveException(self, "Another piece is blocking the way", self.pos, new_pos)

        return new_pos

    def capture(self, capt_pos):
        if self.color == "white":
            mult = -1
        elif self.color == "black":
            mult = 1
        else:
            raise ValueError

        print(capt_pos[1] == self.pos[1])
        if capt_pos[1] == self.pos[1]:
            raise ImpossibleMoveException(self, "Pawn can't move across", self.pos, capt_pos)
        elif capt_pos[1] - mult == self.pos[1] or abs(capt_pos[0] - self.pos[0]) != 1:
            raise ImpossibleMoveException(self, "Pawn can't reach", self.pos, capt_pos)

        return capt_pos

    def piece_attack_check(self, board, king_pos):
        if self.color == "white":
            mult = -1
        else:
            mult = -1

        board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[0] + 1, self.pos[1] + mult)
        board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[0] - 1, self.pos[1] + mult)

