from Errors import JustError

class Piece:
    # A class for Rook
    def __init__(self, board, color: str, pos: tuple[int, int]):
        self.pos = pos  # refers to the coordinates. WILL BE RENAMED

        self.board = board
        # ? add reference to the board?
        self.name = "Rook"
        self.sym = "R"

        self.color = color if color in ("white", "black") else None

    def move(self, new_pos):
        print(f"Moved {self.name} on {self.pos} to {new_pos}")
        self.pos = new_pos

    def reach_check(self, pos: tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        pass

    def blocking_check(self, pos):
        pass

class Rook(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Rook, self).__init__(board, color, pos)

    def reach_check(self, pos: tuple[int, int], en_passan: bool = False) -> tuple[bool, str | None]:
        # Position change. Needed to check if the movement is possible
        pos_change = abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])
        if (pos_change[0] != 0 and pos_change[1] != 0) and sum(pos_change) != 0:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos):
        pos_change = self.pos[0] - pos[0], self.pos[1] - pos[1]
        axis = 0 if pos_change[0] else 1
        points = self.get_line_position(axis, pos_change)
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

    def get_line_position(self, axis: 0 | 1, pos_change):
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
    def construct_rooks(board):
        # A function that adds the rooks to the board
        board.board[0][0] = Rook(board, "white", (0, 0))
        board.board[0][7] = Rook(board, "white", (7, 0))
        board.board[7][0] = Rook(board, "black", (0, 7))
        board.board[7][7] = Rook(board, "black", (7, 7))

