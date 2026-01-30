from Errors import ImpossibleMoveException
from util import pos_to_cord


def construct_queens(board):
    board[0][4] = Queen("white", (4, 0))
    board[7][4] = Queen("black", (4, 7))

    return board


class Queen:
    def __init__(self, color, pos):
        self.pos = pos

        self.name = "Queen"
        self.sym = "Q"

        self.color = color if color in ("white", "black") else None

    def move(self, board, new_pos):
        print(f"New pos: {new_pos}")

        pos_change = abs(self.pos[0] - new_pos[0]), abs(self.pos[1] - new_pos[1])

        if ((pos_change[0] != 0 and pos_change[1] != 0) or not (8 > new_pos[0] > -1 and 8 > new_pos[1] > -1)) and pos_change[0] != pos_change[1]:
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
        mult_x = -1 if self.pos[0] - new_pos[0] > 0 else 1
        mult_y = -1 if self.pos[1] - new_pos[1] > 0 else 1
        print(pos_change)
        print(mult_x, mult_y)

        for i in range(1, pos_change[pos_axes]):
            if pos_change[0] == pos_change[1]:
                if board.board[self.pos[1] + (mult_y * i)][self.pos[0] + (mult_x * i)] != 0:
                    return self.pos[0] + (mult_x * i), self.pos[1] + (mult_y * i)
            elif pos_axes == 0:
                if board.board[self.pos[1]][self.pos[0] + (mult_x * i)] != 0:
                    return self.pos[0] + (mult_x * i), self.pos[1]
            elif pos_axes == 1:
                if board.board[self.pos[1] + (mult_y * i)][self.pos[0]] != 0:
                    return self.pos[0], self.pos[1] + (mult_y * i)

        else:
            return

    def diagonal_attack_check(self, board, x, y):
        if x == 0 or y == 0:
            return

        for i in range(1, 8):
            if board.board[self.pos[1] + (i * y)][self.pos[0] + (i * x)] != 0:
                board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[1] + (i * y), self.pos[0] + (i * x))
            else:
                board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[1] + (i * y), self.pos[0] + (i * x))
                break

    def vertical_attack_check(self, board, x, y):
        for i in range(1, 8):
            if board.board[self.pos[1]][self.pos[0] + (i * x)] != 0 and x == 1:
                board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[0] + (i * x), self.pos[1])
            if board.board[self.pos[1] + (i * y)][self.pos[0]] != 0 and y == 1:
                board.attacking_pos[self.color][(self.name, self.pos)].append(self.pos[0], self.pos[1] + (i * y))

            if board.board[self.pos[1]][self.pos[0] + (i * x)] == 0:
                x = 0
            if board.board[self.pos[1] + (i * y)][self.pos[0]] == 0:
                y = 0

    def piece_attack_check(self, board, king_pos):
        try:
            y = (self.pos[1] - king_pos[1]) // 1
        except ValueError:
            y = 0

        try:
            x = (self.pos[0] - king_pos[0]) // 1
        except ValueError:
            x = 0

        self.diagonal_attack_check(board, x, y)
        self.vertical_attack_check(board, x, y)



