from __future__ import annotations

class PositionVector2D:
    def __init__(self, val: str | tuple[int, int]):
        self.pos: str
        self.cord: tuple[int, int]
        if isinstance(val, str):
#            print("val is str")
            self.cord = val
            self.pos = self.cord_to_pos(val)
#            print(self.pos, self.cord)
        elif isinstance(val, tuple):
#            print("val is tuple[int, int]")
            self.pos = val
            self.cord = self.pos_to_cord(val) if val[0] >= 0 and val[1] >= 0 else ""
#            print(self.pos, self.cord)


    def __sub__(self, other: PositionVector2D | tuple[int, int]):
        if isinstance(other, PositionVector2D):
            res = (self.pos[0] - other.pos[0], self.pos[1] - other.pos[1])
#            print(res)
            return PositionVector2D((self.pos[0] - other.pos[0], self.pos[1] - other.pos[1]))
        elif isinstance(other, tuple):   # add a check if a 1x2 int array
            return PositionVector2D((self.pos[0] - other[0], self.pos[1] - other[1]))

    def __add__(self, other: PositionVector2D | tuple[int, int]):
        if isinstance(other, PositionVector2D):
            return PositionVector2D((self.pos[0] + other.pos[0], self.pos[1] + other.pos[1]))
        elif isinstance(other, tuple):
            return PositionVector2D((self.pos[0] + other[0], self.pos[1] + other[1]))

    def __mul__(self, other: PositionVector2D | tuple[int, int] | int):
        if isinstance(other, int | float):
            return PositionVector2D((self.pos[0] * other, self.pos[1] * other))
        elif isinstance(other, PositionVector2D | tuple):
            return PositionVector2D((self.pos[0] * other[0], self.pos[1] * other[1]))

    def __eq__(self, other):
        if isinstance(other, PositionVector2D):
            return self.pos == other.pos
        elif isinstance(other, tuple):
            return self.pos[0] == other[0] and self.pos[1] == other[1]
        elif isinstance(other, str):
            return self.cord == other
        return False

    # def __getattr__(self, item):
    #     pass
    #     # print(item)
    #     # if item == "pos":
    #     #     return self.pos

    def normalize(self):
        return PositionVector2D((self.sign(self.pos[0]), self.sign(self.pos[1])))

    def in_range(self, upper_b, lower_b):  # do we need it?
        pass


    def __abs__(self):
        return PositionVector2D((abs(self.pos[0]), abs(self.pos[1])))

    def __getitem__(self, item):
        return self.pos[item]

    # think
    # def __setitem__(self, key, value):
    #     self.pos[key] = value

    def __repr__(self):
        return f"{self.pos} ({self.cord})"

    @staticmethod
    def pos_to_cord(pos: PositionVector2D | tuple[int, int]) -> str:
        # A function that changes the text position into a coordinate
        # eg. A1 -> (0,0)
        return "".join((chr(96 - pos[0] + 8), str(pos[1] + 1)))

    @staticmethod
    def cord_to_pos(cord: str) -> PositionVector2D | tuple[int, int]:  # eg. (0, 0)
        # A function that changes the coordinate value to the text position
        # eg. (0,0) -> A1
        return PositionVector2D((7 - (ord(cord[0]) - 97), int(cord[1]) - 1))

    @staticmethod
    def sign(value: int):
        if value < 0:
            return -1
        elif value > 0:
            return 1
        else:
            return 0


#         0     1     2     3     4     5     6     7
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  0   | A1  | B1  | C1  | D1  | ### | F1  | G1  | ### | 7,0 - 4,0 = 3,0
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  1   | A2  | B2  | C2  | D2  | E2  | F2  | G2  | H2  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  2   | A3  | B3  | C3  | D3  | E3  | F3  | G3  | H3  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  3   | A4  | B4  | C4  | D4  | E4  | F4  | G4  | H4  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  4   | A5  | B5  | C5  | D5  | E5  | F5  | G5  | H5  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  5   | A6  | B6  | C6  | D6  | E6  | F6  | G6  | H6  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  6   | A7  | B7  | C7  | D7  | E7  | F7  | G7  | H7  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  7   | A8  | B8  | C8  | D8  | E8  | F8  | G8  | H8  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|

# pos = PositionVector2D((2, 0))
# print(pos.pos, pos.cord)
# add_v = PositionVector2D((4, 5))
# direction = pos - add_v
# print(direction)
# print(direction.normalize())


print(PositionVector2D.pos_to_cord((2, 0)))