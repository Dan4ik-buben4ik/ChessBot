from Errors import ImpossibleMoveException, PieceColorException
from util import cord_to_pos, pos_to_cord


def construct_knights(board):
    board[0][1] = Knight("white", (1, 0))
    board[0][6] = Knight("white", (6, 0))
    board[7][1] = Knight("black", (1, 7))
    board[7][6] = Knight("black", (6, 7))

    return board


class Knight:
    def __init__(self, color, pos):
        self.pos = pos

        self.name = "Knight"
        self.sym = "N"

        self.color = color if color in ("white", "black") else None

    def move(self, new_pos):
        print(f"New pos: {new_pos}")
        # if board.board[new_pos[1]][new_pos[0]] != 0:

        pos_change = abs(self.pos[0] - new_pos[0]), abs(self.pos[1] - new_pos[1])

        if pos_change[0] + pos_change[1] != 3 or (pos_change[0] not in (1, 2) or pos_change[1] not in (1, 2)):
            raise ImpossibleMoveException(self, f"{self.name} can't reach", self.pos, new_pos)
        elif pos_change[0] == 0 and pos_change[1] == 0:
            raise ImpossibleMoveException(self, "Need to move", self.pos, new_pos)

        return new_pos

    def piece_attack_check(self, board, king_pos):
        pos_change = (self.pos[0] - king_pos[0]) // 1, (self.pos[1] - king_pos[1]) // 1
        if 0 <= self.pos[0] + (2 + pos_change[0]) <= 7 and 0 <= self.pos[1] + (1 + pos_change[1]) <= 7:
            board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[0] + (2 + pos_change[0]), self.pos[1] - (1 + pos_change[1]))
        if 0 <= self.pos[0] + (1 + pos_change[0]) <= 7 and 0 <= self.pos[1] + (2 + pos_change[1]) <= 7:
            board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[0] + (1 + pos_change[0]), self.pos[1] + (2 + pos_change[1]))




