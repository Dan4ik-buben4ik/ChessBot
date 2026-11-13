import random
import csv
import enum
import array
import re
import numpy as np
import numpy.random
from typing import TypeAlias
from pathlib import Path

from .file_formats import read_nnue


# Errors
class InvalidMoveException(BaseException):
    def __init__(self, txt):
        super().__init__(txt)

class UnrecognisedSanMove(BaseException):
    def __init__(self, san):
        super().__init__(f"Cant recognise the SAN move [{san}]")

class NotImplementedError(BaseException):
    def __init__(self):
        super().__init__("Haven't implemented yet")


# game results
class GameResult(enum.Enum):
    ONGOING = 0
    CHECKMATE = 1
    STALEMATE = 2
    DRAW_REPETITION = 3
    DRAW_50_MOVES = 4
    DRAW_INSUFFICIENT_MATERIAL = 5


# Constants
# File Related Constants
project_base_dir = Path(__file__).resolve().parent.parent
HALF_KA_NNUE_PATH = project_base_dir / "nn_version_001.nnue"
ENGINE_WEIGHTS_PATH = project_base_dir / "nn_version_001.nnue"
PAWN_CNN_WEIGHTS_PATH = project_base_dir / "pawn_cnn_version_001.nnue"

TRAINING_DATA_80K_PATH = project_base_dir / "TrainingData" / "80kChessData.csv"

MAGIC_TABLE_PATH = Path(__file__).resolve().parent / "magic_table.bin"



# Piece-Square Constants

PieceType: TypeAlias = int
PAWN: PieceType = 1
KNIGHT: PieceType = 2
BISHOP: PieceType = 3
ROOK: PieceType = 4
QUEEN: PieceType = 5
KING: PieceType = 6

PIECE_TYPES = [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]
PIECE_SYM = [None, "p", "n", "b", "r", "q", "k"]
PIECE_NAME = [None, "pawn", "knight", "bishop", "rook", "queen", "king"]

Color: TypeAlias = int
WHITE: Color = 0
BLACK: Color = 1
COLOR_NAME = ["white", "black"]

File: TypeAlias = int
FILE_A: File = 0
FILE_B: File = 1
FILE_C: File = 2
FILE_D: File = 3
FILE_E: File = 4
FILE_F: File = 5
FILE_G: File = 6
FILE_H: File = 7
FILES = [FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H]
FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"]

BB_FILE = 0x0101_0101_0101_0101

Rank: TypeAlias = int
RANK_1: Rank = 0
RANK_2: Rank = 1
RANK_3: Rank = 2
RANK_4: Rank = 3
RANK_5: Rank = 4
RANK_6: Rank = 5
RANK_7: Rank = 6
RANK_8: Rank = 7
RANKS = [RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"]
BB_Rank = 0x0000_0000_0000_0011

BitBoard: TypeAlias = int
BB_EMPTY = 0x0000_0000_0000_0000
BB_ALL = 0xffff_ffff_ffff_ffff

BB_WHITE_SQUARES = 0xaaaa_aaaa_aaaa_aaaa
BB_BLACK_SQUARES = 0x5555_5555_5555_5555

BB_RANK_1: BitBoard = 0xff << (8 * RANK_1)
BB_RANK_2: BitBoard = 0xff << (8 * RANK_2)
BB_RANK_3: BitBoard = 0xff << (8 * RANK_3)
BB_RANK_4: BitBoard = 0xff << (8 * RANK_4)
BB_RANK_5: BitBoard = 0xff << (8 * RANK_5)
BB_RANK_6: BitBoard = 0xff << (8 * RANK_6)
BB_RANK_7: BitBoard = 0xff << (8 * RANK_7)
BB_RANK_8: BitBoard = 0xff << (8 * RANK_8)
BB_RANKS = [BB_RANK_1, BB_RANK_2, BB_RANK_3, BB_RANK_4, BB_RANK_5, BB_RANK_6, BB_RANK_7, BB_RANK_8]

BB_FILE_A: BitBoard = 0x0101_0101_0101_0101 << FILE_A
BB_FILE_B: BitBoard = 0x0101_0101_0101_0101 << FILE_B
BB_FILE_C: BitBoard = 0x0101_0101_0101_0101 << FILE_C
BB_FILE_D: BitBoard = 0x0101_0101_0101_0101 << FILE_D
BB_FILE_E: BitBoard = 0x0101_0101_0101_0101 << FILE_E
BB_FILE_F: BitBoard = 0x0101_0101_0101_0101 << FILE_F
BB_FILE_G: BitBoard = 0x0101_0101_0101_0101 << FILE_G
BB_FILE_H: BitBoard = 0x0101_0101_0101_0101 << FILE_H
BB_FILES = [BB_FILE_A, BB_FILE_B, BB_FILE_C, BB_FILE_D, BB_FILE_E, BB_FILE_F, BB_FILE_G, BB_FILE_H]

BB_CENTRE = 0x0000_0018_1800_00
BB_EXTENDED_CENTRE = 0x0000_3C24_3C24_0000
BB_EDGES = BB_RANK_1 | BB_RANK_8 | BB_FILE_A | BB_FILE_H

Square: TypeAlias = int
A1: Square = 0
B1: Square = 1
C1: Square = 2
D1: Square = 3
E1: Square = 4
F1: Square = 5
G1: Square = 6
H1: Square = 7
A2: Square = 8
B2: Square = 9
C2: Square = 10
D2: Square = 11
E2: Square = 12
F2: Square = 13
G2: Square = 14
H2: Square = 15
A3: Square = 16
B3: Square = 17
C3: Square = 18
D3: Square = 19
E3: Square = 20
F3: Square = 21
G3: Square = 22
H3: Square = 23
A4: Square = 24
B4: Square = 25
C4: Square = 26
D4: Square = 27
E4: Square = 28
F4: Square = 29
G4: Square = 30
H4: Square = 31
A5: Square = 32
B5: Square = 33
C5: Square = 34
D5: Square = 35
E5: Square = 36
F5: Square = 37
G5: Square = 38
H5: Square = 39
A6: Square = 40
B6: Square = 41
C6: Square = 42
D6: Square = 43
E6: Square = 44
F6: Square = 45
G6: Square = 46
H6: Square = 47
A7: Square = 48
B7: Square = 49
C7: Square = 50
D7: Square = 51
E7: Square = 51
F7: Square = 53
G7: Square = 54
H7: Square = 55
A8: Square = 56
B8: Square = 57
C8: Square = 58
D8: Square = 59
E8: Square = 60
F8: Square = 61
G8: Square = 62
H8: Square = 63
SQUARE_NAMES = [f + r for r in RANK_NAMES for f in FILE_NAMES]
SQUARES = list(range(64))

def square_rank(square):
    return square >> 3

def square_file(square):
    return square & 7

# def vertical_flip(bitboard):
#     """
#     takes the bard and flips it vertically
#     """
#     bitboard = ((bitboard >> 8) & 0x00FF00FF00FF00FF) | ((bitboard & 0x00FF00FF00FF00FF) << 8)
#     bitboard = ((bitboard >> 16) & 0x0000FFFF0000FFFF) | ((bitboard & 0x0000FFFF0000FFFF) << 16)
#     bitboard = (bitboard >> 32) | (bitboard << 32)
#     return bitboard

def horizontal_flip_square(square: Square):
    return square ^ 7

def vertical_flip_square(square: Square):
    return square ^ 56



def scan_forward_bb(bitboard):
    """yields squares"""
    while bitboard:
        msb = bitboard.bit_length() - 1
        yield msb

        bitboard ^= 1 << msb

def scan_backward_bb(bitboard):
    """yields squares"""
    while bitboard:
        lsb = bitboard & -bitboard
        square = lsb.bit_length() - 1
        yield square
        bitboard &= bitboard - 1

def square_distance(a: Square, b: Square):
    """in king steps between the squares"""
    return max(abs(square_file(a) - square_file(b)), abs(square_rank(a) - square_rank(b)))


# castling rights
WHITE_KINGS_CASTLE = 1 << 0
WHITE_QUEENS_CASTLE = 1 << 1
BLACK_KINGS_CASTLE = 1 << 2
BLACK_QUEENS_CASTLE = 1 << 3


CASTLING_RIGHTS_UPDATE_BY_SQUARE = {
    A1: WHITE_QUEENS_CASTLE,
    H1: WHITE_KINGS_CASTLE,
    E1: WHITE_QUEENS_CASTLE | WHITE_KINGS_CASTLE,
    A8: BLACK_QUEENS_CASTLE,
    H8: BLACK_KINGS_CASTLE,
    E8: BLACK_QUEENS_CASTLE | BLACK_KINGS_CASTLE,
}


# attacks related rays
def _delta_attacks(square: Square, deltas: list):
    return _sliding_attacks(square, BB_ALL, deltas)


def _sliding_attacks(square: Square, occupied: BitBoard, deltas: list):
    attacks = BB_EMPTY
    for d in deltas:
        sq = square
        while True:
            sq += d
            if not (0 <= sq < 64) or square_distance(sq, sq - d) > 2:
                break

            attacks |= 1 << sq

            if occupied & (1 << sq):
                break

    return attacks

def _edges(sq):
    return (
        ((BB_RANK_1 | BB_RANK_8) & ~BB_RANKS[square_rank(sq)]) |
        ((BB_FILE_A | BB_FILE_H) & ~BB_FILES[square_file(sq)])
    )

def _create_masks(deltas):
    masks = []
    for square in SQUARES:
        mask = _sliding_attacks(square, BB_EMPTY, deltas) & ~_edges(square)
        masks.append(mask)

    return masks




BB_PAWN_ATTACKS: list[list[Square]] = [[_delta_attacks(sq, delta) for sq in SQUARES] for delta in ([7, 9], [-7, -9])]
BB_KNIGHT_ATTACKS: list[Square] = [_delta_attacks(sq, [-10, 6, 15, 17, 10, -6, -17, -15]) for sq in SQUARES]
BB_KING_ATTACKS: list[Square] = [_delta_attacks(sq, [-7, -8, -9, -1, 1, 7, 8, 9]) for sq in SQUARES]
BB_ORTHOGONAL_RAYS: list[BitBoard] = [_sliding_attacks(sq, BB_EMPTY, [8, 1, -1, -8]) for sq in SQUARES]
BB_DIAGONAL_RAYS: list[BitBoard] = [_sliding_attacks(sq, BB_EMPTY, [7, 9, -7, -9]) for sq in SQUARES]

BB_ORTHOGONAL_MASK: list[BitBoard] = _create_masks([8, 1, -1, -8])
BB_DIAGONAL_MASK: list[BitBoard] = _create_masks([7, 9, -7, -9])

# reading the magic number files
with open(MAGIC_TABLE_PATH, "rb") as file:
    ROOK_MAGIC = array.array("Q")
    ROOK_MAGIC.fromfile(file, 64)

    ROOK_SHIFT = array.array("B")
    ROOK_SHIFT.fromfile(file, 64)

    ROOK_ATTACK_OFFSET = array.array("Q")
    ROOK_ATTACK_TABLE = array.array("Q")

    offset = 0
    for sq, shift in enumerate(ROOK_SHIFT):
        size = 1 << (64 - shift)
        ROOK_ATTACK_OFFSET.append(offset)

        attack = array.array("Q")
        attack.fromfile(file, size)

        assert len(attack) == size

        ROOK_ATTACK_TABLE.extend(attack)

        offset += size

    BISHOP_MAGIC = array.array("Q")
    BISHOP_MAGIC.fromfile(file, 64)

    BISHOP_SHIFT = array.array("B")
    BISHOP_SHIFT.fromfile(file, 64)

    BISHOP_ATTACK_OFFSET = array.array("Q")
    BISHOP_ATTACK_TABLE = array.array("Q")

    offset = 0
    for sq, shift in enumerate(BISHOP_SHIFT):
        size = 1 << (64 - shift)
        BISHOP_ATTACK_OFFSET.append(offset)

        attack = array.array("Q")
        attack.fromfile(file, size)

        assert len(attack) == size

        BISHOP_ATTACK_TABLE.extend(attack)

        offset += size


#rays creation
def _between() -> list[list[BitBoard]]:
    rays = []
    for a in range(64):
        bb_a = 1 << a
        temp_list = []
        for b in range(64):
            bb_b = 1 << b
            if BB_ORTHOGONAL_RAYS[a] & bb_b:
                temp_list.append(BB_ORTHOGONAL_RAYS[a] & BB_ORTHOGONAL_RAYS[b] & (BB_ALL << a ^ BB_ALL << b))
            elif BB_DIAGONAL_RAYS[a] & bb_b:
                temp_list.append(BB_DIAGONAL_RAYS[a] & BB_DIAGONAL_RAYS[b] & (BB_ALL << a ^ BB_ALL << b))
            else:
                temp_list.append(BB_EMPTY)

        rays.append(temp_list)

    return rays


BB_BETWEEN = _between()


def _rays() -> list[list[BitBoard]]:
    rays = []
    for a in range(64):
        bb_a = 1 << a
        temp_list = []
        for b in range(64):
            bb_b = 1 << b
            if BB_ORTHOGONAL_RAYS[a] & bb_b:
                temp_list.append(BB_BETWEEN[a][b] | bb_a | bb_b)
            elif BB_DIAGONAL_RAYS[a] & bb_b:
                temp_list.append(BB_BETWEEN[a][b] | bb_a | bb_b)
            else:
                temp_list.append(BB_EMPTY)

        rays.append(temp_list)

    return rays


BB_RAYS = _rays()

#cambinations from a mask

def _subsets(mask):
    subset = mask
    while True:
        yield subset

        if subset == 0:
            break

        subset = (subset-1) & mask


# bit manipulation
def pop_lsb(bitboard):
    lsb = bitboard & -bitboard
    square = lsb.bit_length() - 1
    bitboard &= bitboard - 1

    return square, bitboard


def lsb_square(bitboard):
    return (bitboard & -bitboard).bit_length() - 1

def msb_square(bitboard):
    return bitboard.bit_length() - 1

# san move regex
SAN_REGEX = re.compile(r"^([NBKRQ])?([a-h])?([1-8])?[\-x]?([a-h][1-8])(=?[nbrqkNBRQK])?[\+#]?\Z")

# fen
def vertical_flip_fen(fen):
    """ flips the fen vertically"""
    # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e4 0 1
    new_fen = ""
    sections = fen.split(" ")

    for row in sections[0].split("/")[::-1]:
        for piece in row:
            if piece.isalpha():
                if piece.isupper():
                    piece = piece.lower()
                else:
                    piece = piece.upper()
            new_fen += piece
        new_fen += "/"
    new_fen = new_fen[:-1]
    new_fen += " "

    new_fen += "b " if sections[1] == "w" else "w "

    castling = ""
    if "k" in sections[2]:
        castling += "K"
    if "q" in sections[2]:
        castling += "Q"
    if "K" in sections[2]:
        castling += "k"
    if "Q" in sections[2]:
        castling += "q"

    new_fen += (castling + " ") if castling else "- "

    if sections[3] != "-":
        new_fen += sections[3][0] + str(9 - int(sections[3][1])) + " "
    else:
        new_fen += "- "

    new_fen += sections[4] + " " + sections[5]

    return new_fen

# Useful Classes


# Move class
FROM_OFFSET = 0
TO_OFFSET = 6
PROMOTION_OFFSET = 12

FROM_MASK = 0b111111
TO_MASK = 0b111111
PROMOTION_MASK = 0b111

class BitBoardState:
    __slots__ = (
        "pawns", "knights", "bishops", "rooks", "queens", "kings", "occupancy_white", "occupancy_black", "castling_rights",
        "ep_square", "half_moves", "full_moves", "hash", "turn", "repetition_table", "white_accumulator", "black_accumulator", "pawn_nn",
        "debug_feature_set_white", "debug_feature_set_black",
    )

    def __init__(self):
        self.pawns = 0
        self.knights = 0
        self.bishops = 0
        self.rooks = 0
        self.queens = 0
        self.kings = 0

        self.occupancy_white = 0
        self.occupancy_black = 0
        self.castling_rights = 0
        self.ep_square: Square | None = 0
        self.half_moves = 0
        self.full_moves = 0
        self.hash = 0
        self.turn = 0

        self.repetition_table = {}

        self.white_accumulator = np.zeros((128, 1))
        self.black_accumulator = np.zeros((128, 1))
        self.pawn_nn = np.zeros((8, 1))

        self.debug_feature_set_white = tuple()
        self.debug_feature_set_black = tuple()

    @classmethod
    def from_board(cls, bitboard):
        state = cls()
        state.update(bitboard)
        return state

    def update(self, bitboard):
        self.pawns = bitboard.pawns
        self.knights = bitboard.knights
        self.bishops = bitboard.bishops
        self.rooks = bitboard.rooks
        self.queens = bitboard.queens
        self.kings = bitboard.kings

        self.occupancy_white = bitboard.occupancy_color[0]
        self.occupancy_black = bitboard.occupancy_color[1]
        self.castling_rights = bitboard.castling_rights
        self.ep_square: Square | None = bitboard.ep_square
        self.half_moves = bitboard.half_moves
        self.full_moves = bitboard.full_moves
        self.hash = bitboard.hash
        self.turn = bitboard.turn

        self.repetition_table = bitboard.repetition_table.copy()

        np.copyto(self.white_accumulator, bitboard.nnue[0])
        np.copyto(self.black_accumulator, bitboard.nnue[1])
        np.copyto(self.pawn_nn, bitboard.pawn_nn)

        self.debug_feature_set_white = tuple(bitboard.debug_feature_indexes[0])
        self.debug_feature_set_black = tuple(bitboard.debug_feature_indexes[1])

    def restore(self, bitboard):
        bitboard.pawns = self.pawns
        bitboard.knights = self.knights
        bitboard.bishops = self.bishops
        bitboard.rooks = self.rooks
        bitboard.queens = self.queens
        bitboard.kings = self.kings

        bitboard.occupancy_color = [self.occupancy_white, self.occupancy_black]
        bitboard.castling_rights = self.castling_rights
        bitboard.ep_square = self.ep_square
        bitboard.half_moves = self.half_moves
        bitboard.full_moves = self.full_moves
        bitboard.hash = self.hash

        bitboard.occupancy = self.occupancy_white | self.occupancy_black
        bitboard.turn = self.turn

        bitboard.repetition_table = self.repetition_table.copy()

        bitboard.king_sq = [(self.kings & self.occupancy_white).bit_length()-1, (self.kings & self.occupancy_black).bit_length()-1]
        np.copyto(bitboard.nnue[0], self.white_accumulator)
        np.copyto(bitboard.nnue[1], self.black_accumulator)
        np.copyto(bitboard.pawn_nn, self.pawn_nn)

        bitboard.debug_feature_indexes = [set(self.debug_feature_set_white), set(self.debug_feature_set_black)]

    def __repr__(self):
        return f"{self.hash}"


class Move:
    __slots__ = ("_value",)

    def __init__(self, from_square, to_square, promotion: PieceType = 0):
        self._value = (
            from_square << FROM_OFFSET |
            to_square << TO_OFFSET |
            promotion << PROMOTION_OFFSET
        )

    @property
    def from_square(self):
        return (self._value >> FROM_OFFSET) & FROM_MASK

    @property
    def to_square(self):
        return (self._value >> TO_OFFSET) & TO_MASK

    @property
    def promotion(self):
        return (self._value >> PROMOTION_OFFSET) & PROMOTION_MASK


    @classmethod
    def from_uci(cls, uci):
        if not isinstance(uci, str):
            raise TypeError("Expected input of type String")
        if not (4 <= len(uci) <= 5):
            raise InvalidMoveException(f"Invalid uci {uci}")

        try:
            from_square = SQUARE_NAMES.index(uci[:2])
            to_square = SQUARE_NAMES.index(uci[2:4])
            promotion = PIECE_SYM.index(uci[4]) if len(uci) == 5 else 0
            return cls(from_square, to_square, promotion)
        except ValueError:
            raise InvalidMoveException(f"Invalid uci {uci}")

    def uci(self):
        if self.promotion:
            return SQUARE_NAMES[self.from_square] + SQUARE_NAMES[self.to_square] + PIECE_SYM[self.promotion]
        else:
            return SQUARE_NAMES[self.from_square] + SQUARE_NAMES[self.to_square]

    def __repr__(self):
        return self.uci()


# Zobrist Hashing
class ZobristHasher:
    rng = random.Random(0)
    table = [[[bytes(0) for _ in range(64)] for _ in range(12)] for _ in range(2)]

    used = set()
    for c in range(2):
        for i in range(12):
            for j in range(64):
                # ensures that there are no repeats in teh hashing
                while True:
                    random_bits = rng.getrandbits(64)
                    if random_bits not in used:
                        used.add(random_bits)
                        table[c][i][j] = rng.getrandbits(64)
                        break


    black_turn = rng.getrandbits(64)

    castling_rights = []
    for _ in range(16):
        castling_rights.append(rng.getrandbits(64))

    en_passant = {}
    for i in list(FILES):
        en_passant[i] = rng.getrandbits(64)

    @classmethod
    def hash(cls, bitboard):
        h = 0
        for piece, bb_piece in enumerate([bitboard.pawns, bitboard.knights, bitboard.bishops, bitboard.rooks, bitboard.queens, bitboard.kings]):
            while bb_piece:
                lsb, bb_piece = pop_lsb(bb_piece)
                color = WHITE if bitboard.occupancy_color[WHITE] & 1 << lsb else BLACK
                h ^= cls.table[color][piece][lsb]

        h ^= cls.castling_rights[bitboard.castling_rights]


        h ^= cls.en_passant[bitboard.ep_square % 8] if bitboard.ep_square else 0

        if bitboard.turn == BLACK:
            h ^= cls.black_turn

        return h


    @classmethod
    def get_table_value(cls, color, piece_type, square):
        return cls.table[color][piece_type-1][square]

    @classmethod
    def debug(cls, value):
        for table in cls.table:
            for i, piece_bb in enumerate(table):
                for j in piece_bb:
                    if value == j:
                        print(f"piece in {PIECE_NAME[i+1]} issue")
                        return

        if value in cls.castling_rights:
            print("castling issue")

        elif value in cls.en_passant.values():
            print("en passant issue")

        elif value == cls.black_turn:
            print("turn color issue")

        else:
            print("combined issue")

# -----------------------------------------------------------------------------------------------------------------------------
# Engine Related

# Declaring Constants
INF = np.inf # change to a ridiculously high number later
MATE_SCORE = 100_000
NP_RNG_SEED = 0
def generate_feature_table(rng, shape):
    return rng.random(shape)

def innit_half_ka(file_name):
    arr_dict = read_nnue(file_name)
    return arr_dict["Half_KA_Table"]

"""
128 vector
- features KA - key: Color | piece type | sq | king sq
- checks - key: Color | piece type | square
- pinned - key: Color | piece type | square | from square
- pinner - key: Color | piece type | square | to square
"""
table_rng = np.random.default_rng(NP_RNG_SEED)
try:
    feature_table = innit_half_ka(HALF_KA_NNUE_PATH)
except FileNotFoundError as e:
    feature_table = generate_feature_table(table_rng, (6 * 2 * 64 * 64, 128, 1))
    print(f"Cant find the file, generating random table")

# checks_feature_table = generate_feature_table((2 * 6 * 64))
# pinned_feature_table = generate_feature_table((2 * 6 * 64 * 64))
# pinner_feature_table = generate_feature_table((2 * 6 * 64 * 64))


def build_accumulator(board, color):
    features_vector = np.zeros((128, 1))
    # print(f"accumulator for {COLOR_NAME[color]}")
    # print("adding features")
    for sq in scan_backward_bb(board.occupancy):
        piece_type, piece_color = board.piece_at(sq), board.color_at(sq)
        # print(PIECE_NAME[piece_type], SQUARE_NAMES[sq])

        features_vector += feature_table[Half_KA_Index(color == BLACK, piece_type, piece_color == color, sq, board.king_sq[color])]

    # print(f"end accumulator for {COLOR_NAME[color]}")

    return features_vector

def back_propagation_of_accumulator(board, acc_colour, output_grad, learning_rate):
    for sq in scan_backward_bb(board.occupancy):
        piece_type, piece_color = board.piece_at(sq), board.color_at(sq)

        feature_table[Half_KA_Index(acc_colour==BLACK, piece_type, piece_color==acc_colour, sq, board.king_sq[acc_colour])] -= output_grad * learning_rate

def debug_features_set(board, color):
    debug_set = set()
    king_sq = board.king_sq[color]
    for sq in scan_backward_bb(board.occupancy):
        piece_type, piece_color = board.piece_at(sq), board.color_at(sq)
        debug_set.add(Half_KA_Index(color == BLACK, piece_type, piece_color == color, sq, king_sq))
    return debug_set

def debug_feature_index(index):
    king_sq = index & 0b111111
    piece_square = (index >> 6) & 0b111111
    left = int(index >> 12)
    ally = int(left > 6)
    piece_type = (left % 6) + 1
    print(f"piece type: {PIECE_NAME[piece_type]} | piece square: {SQUARE_NAMES[piece_square]} | ally: {ally} | king sq: {SQUARE_NAMES[king_sq]}")



def Half_KA_Index(flip: bool, piece_type, ally: bool, piece_square, king):
    """

    :param flip: responsible for vertical mirroring (used when the feature is tied to black king)
    :param piece_type: piece type in int
    :param ally: is an ally of the accumulator king colour
    :param piece_square: sq
    :param king: king sq for the accumulator
    :return: index for Half KA features table
    """

    # vertical mirroring
    if flip:
        piece_square ^= 56
        king ^= 56

    # horizontal flip
    if (king & 7) < 4:
        piece_square ^= 7
        king ^= 7

    # print(
    #     f"piece type: {PIECE_NAME[piece_type]} | piece square: {SQUARE_NAMES[piece_square]} | ally color: {ally} | king sq: {SQUARE_NAMES[king]}")
    return (
        ((ally * 6) + piece_type-1) << 12 |
        piece_square << 6 |
        king
    )


def bitboards_to_plane(*bitboards):
    depth = len(bitboards)
    plane = np.zeros((depth, 64), dtype=np.float32)
    for i, bb in enumerate(bitboards):
        for j in scan_backward_bb(bb):
            plane[i, j] = 1
    return plane.reshape(depth, 8, 8)

# -------------------------------------------------------------------------------------------------------------------------------------
# nn training related

# Eg of usage
# bat = DataBatcher("chessData.csv")
# bat.segregate_by_eval(pos_number=700_000)
# bat.lengths()
# lengths = [int(input(f"length {i+1}: ")) for i in range(4)]
# bat.save(lengths, "80kChessData.csv")
class DataBatcher:  # think about making it to help others later
    def __init__(self, dataset_path, ):
        self.path = dataset_path
        self.groups = {
            "winning": [],
            "large_advantage": [],
            "small_advantage": [],
            "equal": [],
        }

    def segregate_by_eval(self, pos_number= 1):
        with open(self.path, "r") as puzzles:
            puzzle_reader = csv.reader(puzzles, delimiter=",")
            next(puzzle_reader)
            missed = 0
            for index, puzzle in enumerate(puzzle_reader):
                if index-missed >= pos_number:
                    break

                if puzzle[1].startswith("#"):
                    missed +=1
                    continue
                fen = puzzle[0]
                val = int(puzzle[1])

                if val < -1000 or val > 1000:
                    self.groups["winning"].append(puzzle)
                elif val < -300 or val > 300:
                    self.groups["large_advantage"].append(puzzle)
                elif val < -100 or val > 100:
                    self.groups["small_advantage"].append(puzzle)
                else:
                    self.groups["equal"].append(puzzle)

        # for item in self.groups.values():
        #     random.shuffle(item)

    def lengths(self):
        for g in self.groups.values():
            print(len(g))

    def save(self, lengths, file_path):
        prep_data = []
        for i, g in enumerate(self.groups.values()):
            for j in range(lengths[i]):
                try:
                    prep_data.append(g[j])
                    fen_flip = vertical_flip_fen(g[j][0])
                    target_flip = str(int(g[j][1]) * -1)
                    prep_data.append((fen_flip, target_flip))
                except IndexError:
                    break
        print("shuffling data")
        random.shuffle(prep_data)



        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["fen", "evaluation"])
            writer.writerows(prep_data)









# -----------------------------------------------------------------------------------------------------------------------------
#debug
def bitprint(bit, length=64):
    txt = bin(bit)[2:]
    if len(txt) != length:
        txt = "".join(("0" * (length - len(txt)), txt))
    txt = "\n".join([txt[i:i+8] for i in range(0, len(txt), 8)])
    print(txt)


def bit_string(bit, length=64):
    txt = ""
    while bit:
        txt += str(bit & 0b1)
        bit >>= 1

    if length and len(txt) < length:
        txt += "0" * (length - len(txt))
    return "".join(("0b", txt[::-1]))



