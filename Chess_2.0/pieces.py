

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
        points = self.get_line_position()
        # Checks if there is a piece on the way

    def get_line_position(self, axis: 0 | 1, pos_change):
        # axis can only be x: 0 | y: 1
        if pos_change[axis] < 0:
            points_change = range(pos_change-1, 0, -1)
        elif pos_change[axis] > 0:
            points_change = range(1, pos_change, -1)
        else:
            raise BaseException

        points_axis = list(map(lambda p: p + self.pos[axis], points_change))

        points = [self.pos[0], self.pos[1]]
        points[axis] = points_axis
        return points
