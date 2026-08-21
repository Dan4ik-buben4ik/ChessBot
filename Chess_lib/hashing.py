import random
from .util import *



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

    castling_rights = {
        WHITE_QUEENS_CASTLE: rng.getrandbits(64),
        WHITE_KINGS_CASTLE: rng.getrandbits(64),
        BLACK_QUEENS_CASTLE: rng.getrandbits(64),
        BLACK_KINGS_CASTLE: rng.getrandbits(64),
    }
    castling_rights[WHITE_QUEENS_CASTLE | WHITE_KINGS_CASTLE] = castling_rights[WHITE_QUEENS_CASTLE] ^ castling_rights[WHITE_KINGS_CASTLE]
    castling_rights[BLACK_QUEENS_CASTLE | BLACK_KINGS_CASTLE] = castling_rights[BLACK_QUEENS_CASTLE] ^ castling_rights[BLACK_KINGS_CASTLE]

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

        if bitboard.castling_rights & WHITE_QUEENS_CASTLE:
            h ^= cls.castling_rights[WHITE_QUEENS_CASTLE]
        if bitboard.castling_rights & WHITE_KINGS_CASTLE:
            h ^= cls.castling_rights[WHITE_KINGS_CASTLE]
        if bitboard.castling_rights & BLACK_QUEENS_CASTLE:
            h ^= cls.castling_rights[BLACK_QUEENS_CASTLE]
        if bitboard.castling_rights & BLACK_KINGS_CASTLE:
            h ^= cls.castling_rights[BLACK_KINGS_CASTLE]

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

        if value in cls.castling_rights.values():
            print("castling issue")

        elif value in cls.en_passant.values():
            print("en passant issue")

        elif value == cls.black_turn:
            print("turn color issue")

        else:
            print("combined issue")

