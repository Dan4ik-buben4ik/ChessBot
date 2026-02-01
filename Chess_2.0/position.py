class PositionVector2D:
    def __init__(self, val: str | tuple[int, int]):
        if val is str:
            self.pos = val
            self.cord = self.pos_to_cord(val)
        elif val is tuple[int, int]:
            self.cord = val
            self.pos = self.cord_to_pos(val)

    def __sub__(self, other):
        if other is PositionVector2D:
            return PositionVector2D((self.cord[0] - other.cord[0], self.cord[1] - other.cord[1]))
        elif other is tuple[int, int]:
            return PositionVector2D((self.cord[0] - other[0], self.cord[1] - other[1]))

    def __add__(self, other):
        if other is PositionVector2D:
            return PositionVector2D((self.cord[0] + other.cord[0], self.cord[1] + other.cord[1]))
        elif other is tuple[int, int]:
            return PositionVector2D((self.cord[0] + other[0], self.cord[1] + other[1]))

    def normalize(self):
        return self.sign(self.cord[0]), self.sign(self.cord[1])

    def __abs__(self):
        return PositionVector2D((abs(self.cord[0]), abs(self.cord[1])))

    @staticmethod
    def pos_to_cord(pos: tuple[int, int]) -> str:
        # A function that changes the text position into a coordinate
        # eg. A1 -> (0,0)
        return "".join((chr(96 - pos[0] + 8), str(pos[1] + 1)))

    @staticmethod
    def cord_to_pos(cord: str) -> tuple[int, int]:  # eg. (0, 0)
        # A function that changes the coordinate value to the text position
        # eg. (0,0) -> A1
        return 7 - (ord(cord[0]) - 97), int(cord[1]) - 1

    @staticmethod
    def sign(value: int):
        if value < 0:
            return -1
        elif value > 0:
            return 1
        else:
            return 0

