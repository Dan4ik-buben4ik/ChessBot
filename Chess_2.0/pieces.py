from Errors import JustError
from types import GeneratorType
class Piece:
    # A class for Rook
    def __init__(self, board, color: str, pos: tuple[int, int]):
        self.pos = pos  # refers to the coordinates. WILL BE RENAMED

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

    def blocking_check(self, pos):
        pass

    @staticmethod
    def construct(board):
        pass

class Rook(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Rook, self).__init__(board, color, pos)
        self.name = "Rook"
        self.sym = "R"

    def reach_check(self, pos: tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        # doesn't needed
        # Position change. Needed to check if the movement is possible
        pos_change = abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])
        if pos_change[0] != 0 or pos_change[1] != 0:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos):
        pos_change = self.pos[0] - pos[0], self.pos[1] - pos[1]
        axis = 0 if pos_change[0] else 1
        points = self.get_line_positions(axis, pos_change)
        if axis == 0:
            for i in points:
                res = self.board.board[self.pos[1]][i]
                if res is Piece:
                    return True
        if axis == 1:
            for i in points:
                res = self.board.board[i][self.pos[0]]
                if res is Piece:
                    return True
        # Checks if there is a piece on the way

    def get_line_positions(self, axis: 0 | 1, pos_change):
        # axis can only be x: 0 | y: 1
        if pos_change[axis] < 0:
            points_change = range(pos_change[axis]-1, 0, -1)
        elif pos_change[axis] > 0:
            points_change = range(1, pos_change[axis], -1)
        else:
            raise JustError

        points_axis = list(map(lambda p: p + self.pos[axis], points_change))


        return points_axis

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
