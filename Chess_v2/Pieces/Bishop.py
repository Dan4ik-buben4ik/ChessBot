from Errors import ImpossibleMoveException, PieceColorException
from util import cord_to_pos, pos_to_cord


def construct_bishops(board):
    board[0][2] = Bishop("white", (2, 0))
    board[0][5] = Bishop("white", (5, 0))
    board[7][2] = Bishop("black", (2, 7))
    board[7][5] = Bishop("black", (5, 7))

    return board


class Bishop:
    def __init__(self, color, pos):
        self.pos = pos

        self.name = "Bishop"
        self.sym = "B"

        self.color = color if color in ("white", "black") else None

    def move(self, board, new_pos):
        print(f"New pos: {new_pos}")
        # if board.board[new_pos[1]][new_pos[0]] != 0:

        pos_change = abs(self.pos[0] - new_pos[0]), abs(self.pos[1] - new_pos[1])

        if pos_change[0] != pos_change[1]:
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
        mult_x = -1 if self.pos[0] - new_pos[0] > 0 else 1
        mult_y = -1 if self.pos[1] - new_pos[1] > 0 else 1
        # print(self.pos, new_pos)
        # print(mult_x, mult_y)
        # print(pos_change)

        for i in range(1, pos_change[0]):
            print(self.pos[0] + (mult_y * i), self.pos[1] + (mult_x * i))
            print((mult_x * i), (mult_y * i))
            if board.board[self.pos[1] + (mult_y * i)][self.pos[0] + (mult_x * i)] != 0:
                return self.pos[0] + (mult_x * i), self.pos[1] + (mult_y * i)
        else:
            return

    def piece_attack_check(self, board, king_pos):
        try:
            y = (self.pos[1] - king_pos[1]) // 1
        except ValueError:
            return

        try:
            x = (self.pos[0] - king_pos[0]) // 1
        except ValueError:
            return

        for i in range(1, 8):
            if board.board[self.pos[1] + (i * y)][self.pos[0] + (i * x)] != 0:
                board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[1] + (i * y), self.pos[0] + (i * x))
            else:
                board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[1] + (i * y), self.pos[0] + (i * x))
                break
