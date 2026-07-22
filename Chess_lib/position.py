from __future__ import annotations

class PositionVector2D:
    """ A class responsible for storing and manipulating the board squares

    :ivar _position: the coordinate position of the square
    :type _position: tuple[int, int]
    """

    def __init__(self, val: str | tuple[int, int]):
        """ An initialization of the class instance """
        self._position: tuple[int, int]
        if isinstance(val, str):
            self._position = self.from_algebraic(val)

        elif isinstance(val, tuple):
            self._position = val

    @property
    def position(self):
        """ PositionVector2D._position

        :type: tuple[int, int]
        """
        return self._position

    @property
    def algebraic(self):
        """ Algebraic coordinate notation (eg. a1)

        :type: str
        """
        return self.to_algebraic(self._position)


    def __sub__(self, other: PositionVector2D | tuple[int, int]):
        """ Performs vector subtraction

        Enables subtraction operation (PositionVector2D - PositionVector2D) or (PositionVector2D - tuple[int, int])

        :param other: the vector subtracted
        :type other: PositionVector2D | tuple[int, int]

        :return: difference between 2 vectors
        :rtype: PositionVector2D
        """
        if isinstance(other, PositionVector2D):
            res = (self._position[0] - other._position[0], self._position[1] - other._position[1])
#            print(res)
            return PositionVector2D((self._position[0] - other._position[0], self._position[1] - other._position[1]))
        elif isinstance(other, tuple):   # add a check if a 1x2 int array
            return PositionVector2D((self._position[0] - other[0], self._position[1] - other[1]))

    def __add__(self, other: PositionVector2D | tuple[int, int]):
        """ Performs vector addition

        Enables subtraction operation (PositionVector2D + PositionVector2D) or (PositionVector2D + tuple[int, int])

        :param other: the vector added
        :type other: PositionVector2D | tuple[int, int]

        :return: sum of the 2 vectors
        :rtype: PositionVector2D
        """
        if isinstance(other, PositionVector2D):
            return PositionVector2D((self._position[0] + other._position[0], self._position[1] + other._position[1]))
        elif isinstance(other, tuple):
            return PositionVector2D((self._position[0] + other[0], self._position[1] + other[1]))

    def __mul__(self, other: int):
        """ performs an enlargement by a scale factor

        Enables subtraction operation (PositionVector2D * PositionVector2D) or (PositionVector2D * int)

        :param other: the scale factor
        :type other: int

        :return: the enlarged vector
        :rtype: PositionVector2D
        """
        if isinstance(other, int):
            return PositionVector2D((self._position[0] * other, self._position[1] * other))

    def __eq__(self, other):
        """ performs a comparison between 2 vectors

        :param other: the vector compared to
        :type other: PositionVector2D | tuple[int, int]

        :return: whether they are the same or different
        :rtype: bool
        """
        if isinstance(other, PositionVector2D):
            return self._position == other._position
        elif isinstance(other, tuple):
            return self._position[0] == other[0] and self._position[1] == other[1]
        elif isinstance(other, str):
            return self.algebraic == other
        return False

    def __neg__(self):
        """ changes the direction of the vector

        :return: a vector with the opposite direction to the current one
        :rtype: PositionVector2D
        """
        return PositionVector2D((-self._position[0], -self._position[1]))

    def normalize(self):
        """ returns the unit vector

        :return: unit vector
        :rtype: PositionVector2D
        """
        return PositionVector2D((self.sign(self._position[0]), self.sign(self._position[1])))


    def __abs__(self):
        """ makes the coordinate values absolute (positive)

        :return: positive vector
        :rtype: PositionVector2D
        """
        return PositionVector2D((abs(self._position[0]), abs(self._position[1])))

    def __getitem__(self, item):
        """ finds the x/y coordinate via indexing

        :param item: the index for the value
        :type: int

        :return: the x/y value of the vector
        :rtype: int
        """
        return self._position[item]

    def __repr__(self):
        """ representation of the square/vector

        :return: the representation
        :rtype: str
        """
        return f"{self._position} ({self.algebraic})"

    @staticmethod
    def to_algebraic(pos: PositionVector2D | tuple[int, int]) -> str:
        """ A function that converts the position tuple into an algebraic coordinate

        It does so mathematically
        eg. a8 -> (0,0); a = 97 ASCII

        :param pos: the cartesian coordinates
        :type pos: PositionVector2D | tuple[int, int]

        :return: the algebraic coordinate
        :rtype: str
        """
        return "".join((chr(97 + pos[0]), str(8 - pos[1])))

    @staticmethod
    def from_algebraic(algebraic: str) -> PositionVector2D | tuple[int, int]:  # eg. (0, 0)  # rename to "to_algebraic"?
        """ A function that converts an algebraic coordinate into a cartesian coordinate

        It does so mathematically
        # eg. (0,0) -> a8

        :param algebraic: the algebraic coordinate
        :type: str

        :return: the new class instance
        :rtype: PositionVector2D
        """
        return PositionVector2D((ord(algebraic[0]) - 97, 8 - int(algebraic[1])))

    @staticmethod
    def sign(value: int | float):
        """ gives the sign of the number (aka, positive, negative or 0)

        :param value: a number
        :type: int | float

        :return: positive/negative 1 or 0
        :rtype: int
        """
        if value < 0:
            return -1
        elif value > 0:
            return 1
        else:
            return 0

    @staticmethod
    def is_algebraic(cord):
        """ checks if the coordinate in the algebraic chess notation

        :param cord: the coordinate
        :type: str

        :return: True/False
        :rtype: bool
        """
        return len(cord) == 2 and cord[0].isalpha() and cord[1].isdigit()







#                       black
#         0     1     2     3     4     5     6     7
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  0   | A8  | B8  | C8  | D8  | E8  | F8  | G8  | H8  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  1   | A7  | B7  | C7  | D7  | E7  | F7  | G7  | H7  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  2   | A6  | B6  | C6  | D6  | E6  | F6  | G6  | H6  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  3   | A5  | B5  | C5  | D5  | E5  | F5  | G5  | H5  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  4   | A4  | B4  | C4  | D4  | E4  | F4  | G4  | H4  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  5   | A3  | B3  | C3  | D3  | E3  | F3  | G3  | H3  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  6   | A2  | B2  | C2  | D2  | E2  | F2  | G2  | H2  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  7   | A1  | B1  | C1  | D1  | ### | F1  | G1  | H1  | l= 4 r= 3; dir = -1, 0
#      |-----|-----|-----|-----|-----|-----|-----|-----|

# pos = PositionVector2D((2, 0))
# print(pos.pos, pos.cord)
# add_v = PositionVector2D((4, 5))
# direction = pos - add_v
# print(direction)
# print(direction.normalize())
