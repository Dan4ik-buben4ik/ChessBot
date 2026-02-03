from Errors import JustError
from position import PositionVector2D

from types import GeneratorType


class Piece:
    # A class for Rook
    def __init__(self, board, color: str, pos: tuple[int, int]):
        if isinstance(pos, PositionVector2D):
            self.pos = pos
        else:
            self.pos = PositionVector2D(pos)

        self.board = board
        # ? add reference to the board?
        self.name: str
        self.sym: str

        self.color = color if color in ("white", "black") else None

    def move(self, new_pos):
        print(f"Moved {self.name} on {self.pos} to {new_pos}")
        self.pos = new_pos

    def reach_check(self, pos: tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        pass

    def blocking_check(self, pos) -> tuple[bool, str | None]:
        pass

    def around_pos_attack_check(self, pos):  # used to compute if the positions around king are attacked
        pass

    @staticmethod
    def construct(board):
        pass

class Rook(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Rook, self).__init__(board, color, pos)
        self.name = "Rook"
        self.sym = "R"

    def reach_check(self, pos: PositionVector2D | tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        # doesn't needed
        # Position change. Needed to check if the movement is possible
        pos_change = abs(self.pos - pos)
        if pos_change[0] != 0 or pos_change[1] != 0:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = (self.pos - pos) * -1  # == pos - self.pos
        # \/ change using class for pos \/
        direction = pos_change.normalize()
        points = self.get_line_positions(direction, pos_change)
        print(f"blocking check in Rook")
        for i in points:
            piece = self.board.board[i[1]][i[0]]
#            print(i)
#            print(self.board.board[i[1]][i[0]])

# address the issue of not checking last piece and colour. IF it is same colour: return False
#             if i == points[-1] and piece.color == "black":
#                 print("err")
            if piece:
                return True, f"a piece ({piece} is blocking the way on {i}"

        return False, None

        # Checks if there is a piece on the way

    def get_line_positions(self, direction: PositionVector2D | tuple[int, int], pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:

    #    print(f"direction: {direction} ({type(direction)})\npos_change: {pos_change}")

        for i in range(1, max(abs(pos_change))):  # address the issue of last piece not being checked
    #        print(f"Rook.get_line_position(): yield {self.pos + direction * i}, d * i = {direction * i}")
            yield self.pos + direction * i


    def around_pos_attack_check(self, pos):
        pos_change = pos - self.pos
        # \/ change using class for pos \/
        # direction = pos_change[0] // abs(pos_change[0]), 0 if abs(pos_change[0]) > abs(pos_change[1]) else 0, pos_change[1] // abs(pos_change[1])
        direction = pos_change.normalize()
        if direction[0] > direction[1]:
            direction[1] = 0
        else:
            direction[0] = 0

        pos_boarder_change = abs(direction) * 7  # pos_change from pos to boarder in the needed direction

        points = self.get_line_positions(direction, pos_boarder_change)

        print(f"around_pos_attack_check for {self.name}")
        print(f"points: {points}")
        for p in points:
            delta_p = pos - p
            if delta_p[0] in (-1, 0, 1) and delta_p[1] in (-1, 0, 1):
                yield p





    @staticmethod
    def construct(board):
        # A function that adds the rooks to the board
        board.board[0][0] = Rook(board, "white", (0, 0))
        board.board[0][7] = Rook(board, "white", (7, 0))
        board.board[7][0] = Rook(board, "black", (0, 7))
        board.board[7][7] = Rook(board, "black", (7, 7))

class Bishop(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Bishop, self).__init__(board, color, pos)
        self.name = "Bishop"
        self.sym = "B"

    def reach_check(self, pos: tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        # Position change. Needed to check if the movement is possible
        pos_change = abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])
        if (pos_change[0] != 0 and pos_change[1] != 0) and pos_change[0] == pos_change[1]:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos):
        pos_change = self.pos[0] - pos[0], self.pos[1] - pos[1]
        direction = pos_change[0] // 1, pos_change[1] // 1
        axis = 0 if pos_change[0] else 1

        points = self.get_diagonal_positions(pos_change, direction)
        for i in points:
            res = self.board.board[i[0]][i[1]]
            if res is Piece:
                return True

        # Checks if there is a piece on the way

    def get_diagonal_positions(self, pos_change, direction) -> GeneratorType:  # tuple[int, int]
        for i in range(abs(pos_change[0])):
            yield self.pos[0] + i * direction[0], self.pos[1] + i * direction[1]

    @staticmethod
    def construct(board):
        board.board[0][2] = Bishop(board, "white", (2, 0))
        board.board[0][5] = Bishop(board, "white", (5, 0))
        board.board[7][2] = Bishop(board, "black", (2, 7))
        board.board[7][5] = Bishop(board, "black", (5, 7))

class King(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(King, self).__init__(board, color, pos)
        self.name = "King"
        self.sym = "K"
        self.blocked_list = [
            [False, False, False],
            [False, None,  False],
            [False, False, False]
        ]

    def reach_check(self, pos: tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        # Position change. Needed to check if the movement is possible
        pos_change = abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])
        if (pos_change[0] != 0 and pos_change[1] != 0) and (pos_change[0] == 1 or pos_change[1] == 1):
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos):
        # in case of king, this will check whether the space he wants to go is free.
        pos_change = self.pos[0] - pos[0], self.pos[1] - pos[1]
        direction = pos_change
        return self.blocked_list[direction[1]+1][direction[0]+1]

    def move(self, new_pos):
        print(f"Moved {self.name} on {self.pos} to {new_pos}")
        self.pos = new_pos

    def update_blocked_list(self, new_pos):
        for y, row in enumerate(self.board.board):
            for x, piece in enumerate(row):
                pos_change = new_pos[0] - x, new_pos[1] - y
                if piece is self:
                    pass
                elif piece.color == self.color and (pos_change[0] in (-1, 0, 1) and pos_change[0] in (-1, 0, 1)):
                    self.blocked_list[pos_change[1]+1][pos_change[0]+1] = True
                else:  # implement a function for the pieces to find the closest path to king and check if it is near
                    pass

    @staticmethod
    def construct(board):
        board.board[0][3] = King(board, "white", (3, 0))
        board.board[7][3] = King(board, "black", (3, 7))



