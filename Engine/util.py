import enum


class TTFlag(enum.Enum):
    UPPER_BOUND = 0
    LOWER_BOUND = 1
    EXACT = 2


class TTEntree:
    def __init__(self, depth, score, flag, best_move):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move


class PieceType(enum.Enum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

class Color(enum.Enum):
    WHITE = 0
    BLACK = 1

class Square(enum.IntEnum):
    A1 = 0
    B1 = 1
    C1 = 2
    D1 = 3
    E1 = 4
    F1 = 5
    G1 = 6
    H1 = 7
    A2 = 8
    B2 = 9
    C2 = 10
    D2 = 11
    E2 = 12
    F2 = 13
    G2 = 14
    H2 = 15
    A3 = 16
    B3 = 17
    C3 = 18
    D3 = 19
    E3 = 20
    F3 = 21
    G3 = 22
    H3 = 23
    A4 = 24
    B4 = 25
    C4 = 26
    D4 = 27
    E4 = 28
    F4 = 29
    G4 = 30
    H4 = 31
    A5 = 32
    B5 = 33
    C5 = 34
    D5 = 35
    E5 = 36
    F5 = 37
    G5 = 38
    H5 = 39
    A6 = 40
    B6 = 41
    C6 = 42
    D6 = 43
    E6 = 44
    F6 = 45
    G6 = 46
    H6 = 47
    A7 = 48
    B7 = 49
    C7 = 50
    D7 = 51
    E7 = 51
    F7 = 53
    G7 = 54
    H7 = 55
    A8 = 56
    B8 = 57
    C8 = 58
    D8 = 59
    E8 = 60
    F8 = 61
    G8 = 62
    H8 = 63


class File(enum.IntEnum):
    A = 0,
    B = 1,
    C = 2,
    D = 3,
    E = 4,
    F = 5,
    G = 6,
    H = 7

BB_FILE = 0x0101_0101_0101_0101

WHITE_KINGS_CASTLE = 1 << 0
WHITE_QUEENS_CASTLE = 1 << 1
BLACK_KINGS_CASTLE = 1 << 2
BLACK_QUEENS_CASTLE = 1 << 3

class NotImplementedError(BaseException):
    def __init__(self):
        super().__init__("Haven't implemented yet")