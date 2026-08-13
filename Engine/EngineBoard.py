from util import *
from converter import *
from Chess_lib import Board


from functools import reduce
import random



class EngineBoard:
    piece_ID = {
        (Color.WHITE, PieceType.PAWN): 0,
        (Color.WHITE, PieceType.KNIGHT): 1,
        (Color.WHITE, PieceType.BISHOP): 2,
        (Color.WHITE, PieceType.ROOK): 3,
        (Color.WHITE, PieceType.QUEEN): 4,
        (Color.WHITE, PieceType.KING): 5,
        (Color.BLACK, PieceType.PAWN): 6,
        (Color.BLACK, PieceType.KNIGHT): 7,
        (Color.BLACK, PieceType.BISHOP): 8,
        (Color.BLACK, PieceType.ROOK): 9,
        (Color.BLACK, PieceType.QUEEN): 10,
        (Color.BLACK, PieceType.KING): 11,
    }


    pieces_BB = [0 for _ in range(12)]

    WHITE_KING_CASTLE = 1 << 0

    white_occupancy = 0
    black_occupancy = 0
    occupancy = 0

    turn = Color.WHITE

    castling_rights = 0
    possible_en_passant: Square | None = None

    half_moves = 0
    full_moves = 1

    hash = 0

    history = 0

    def from_board(self, board: Board):
        # translates the pieces onto board
        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue

                square = position_vector_converter(piece.pos)
                piece_type = None
                piece_color = None

                index = self.piece_ID[(piece_color, piece_type)]
                self.pieces_BB[index] |= 1 << square

        self._update_occupancy()

        self.turn = turn_color_converter(board.turn)

        if board.castling_rights[Color.WHITE][0]:
            self.castling_rights |= WHITE_QUEENS_CASTLE
        if board.castling_rights[Color.WHITE][1]:
            self.castling_rights |= WHITE_KINGS_CASTLE
        if board.castling_rights[Color.BLACK][0]:
            self.castling_rights |= BLACK_QUEENS_CASTLE
        if board.castling_rights[Color.BLACK][1]:
            self.castling_rights |= BLACK_KINGS_CASTLE

        self.possible_en_passant = position_vector_converter(board.possible_en_passant) if board.possible_en_passant else None

        self.half_moves = board.half_moves
        self.full_moves = board.full_moves

        self.hash = board.hash

    def from_fen(self, fen: str):
        raise NotImplementedError




    def _update_occupancy(self):
        self.white_occupancy = int(reduce(lambda x, y: x | y, self.pieces_BB[:6]))

        self.black_occupancy = int(reduce(lambda x, y: x | y, self.pieces_BB[6:]))

        self.occupancy = self.white_occupancy | self.black_occupancy



# class ZobristHasher:
#     rng = random.Random(0)
#
#     pieces = {
#         (Color.WHITE, PieceType.PAWN): 0,
#         (Color.WHITE, PieceType.KNIGHT): 1,
#         (Color.WHITE, PieceType.BISHOP): 2,
#         (Color.WHITE, PieceType.ROOK): 3,
#         (Color.WHITE, PieceType.QUEEN): 4,
#         (Color.WHITE, PieceType.KING): 5,
#         (Color.BLACK, PieceType.PAWN): 6,
#         (Color.BLACK, PieceType.KNIGHT): 7,
#         (Color.BLACK, PieceType.BISHOP): 8,
#         (Color.BLACK, PieceType.ROOK): 9,
#         (Color.BLACK, PieceType.QUEEN): 10,
#         (Color.BLACK, PieceType.KING): 11,
#     }
#
#     table = [[bytes(0) for _ in range(64)] for _ in range(12)]
#     en_passant = {}
#
#     used = set()
#     for i in range(12):
#         for j in range(64):
#             # ensures that there are no repeats in teh hashing
#             while True:
#                 random_bits = rng.getrandbits(64)
#                 if random_bits not in used:
#                     used.add(random_bits)
#                     table[i][j] = rng.getrandbits(64)
#                     break
#
#
#     black_turn = rng.getrandbits(64)
#
#     castling_rights = {
#         WHITE_QUEENS_CASTLE: rng.getrandbits(64),
#         WHITE_KINGS_CASTLE: rng.getrandbits(64),
#         BLACK_QUEENS_CASTLE: rng.getrandbits(64),
#         BLACK_KINGS_CASTLE: rng.getrandbits(64),
#     }
#
#     for i in list(File):
#         en_passant[i] = rng.getrandbits(64)
#
#     @classmethod
#     def hash(cls, bitboard):
#         raise NotImplementedError
#
#
#     @classmethod
#     def get_table_value(cls, color, piece_type, square):
#         index = cls.pieces[(color, piece_type)]
#         return cls.table[index][square]