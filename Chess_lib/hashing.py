import random
from .util import TurnColor

class ZobristHasher:
    """ A hashing class designed to use Zobrist hashing

    This means converting the entire board into a single 64 bit integer
    and performing xor operations to keep the uniqueness of the position

    the main attribute table would store all the possible piece-position values
    eg. knight on f3 could have a value 12345678 while the same knight on g3 will be 987654321

    Attributes:

    :var rng: a random generator object needed to create the random values for the table
    :type rng: random.Random

    :var pieces: a table with pieces and their colors used as indexes for the table with random values for each piece
    :type pieces: dict[str, int]

    :var table: the main attribute of the class. Stores random 64 bit values for every scenario possible. Dimension: 12 x 64
    :type table: list[list[int]]

    :var black_turn: stores the 64bit value for the turn color
    :type black_turn: int

    :var castling_rights: a dictionary that mimics the board attribute castling_rights, holding the bool values for possible castling
    :type castling_rights: dict[util.TurnColor, list[int]]

    :var en_passant: holds the en passant values for the columns (aka. a->h)
    :type en_passant: dict[str, int]


    """
    rng = random.Random(0)

    pieces = {
            "WHITE_PAWN": 0,
            "WHITE_KNIGHT": 1,
            "WHITE_BISHOP": 2,
            "WHITE_ROOK": 3,
            "WHITE_QUEEN": 4,
            "WHITE_KING": 5,
            "BLACK_PAWN": 6,
            "BLACK_KNIGHT": 7,
            "BLACK_BISHOP": 8,
            "BLACK_ROOK": 9,
            "BLACK_QUEEN": 10,
            "BLACK_KING": 11,

        }

    table = [[bytes(0) for _ in range(64)] for _ in range(12)]
    black_turn = 0
    castling_rights = {}
    en_passant = {}

    used = set()
    for i in range(12):
        for j in range(64):
            # ensures that there are no repeats in teh hashing
            while True:
                random_bits = rng.getrandbits(64)
                if random_bits not in used:
                    used.add(random_bits)
                    table[i][j] = rng.getrandbits(64)
                    break

    black_turn = rng.getrandbits(64)

    castling_rights[TurnColor.WHITE] = [rng.getrandbits(64), rng.getrandbits(64)]
    castling_rights[TurnColor.BLACK] = [rng.getrandbits(64), rng.getrandbits(64)]

    for i in range(8):
        en_passant[chr(97 + i)] = rng.getrandbits(64)

    @classmethod
    def hash(cls, board):
        """ the main function that hashes the board

        This function only encodes the board. Then, the board must be updated manually
        All the updates are done via xor operator, as a xor b xor b == a

        :param board: the board instance that gets hashed
        :type board: loader.Board

        :return: a unique 64bit hash value
        :rtype: int
        """
        h = 0
        for row in board.board:
            for piece in row:
                if piece != 0:
                    i = cls.pieces[f"{piece.color.name}_{piece.name.upper()}"]
                    h ^= cls.table[i][piece.pos[0] + piece.pos[1] * 8]

        if board.castling_rights[TurnColor.WHITE][0]:
            h ^= cls.castling_rights[TurnColor.WHITE][0]
        if board.castling_rights[TurnColor.WHITE][1]:
            h ^= cls.castling_rights[TurnColor.WHITE][1]
        if board.castling_rights[TurnColor.BLACK][0]:
            h ^= cls.castling_rights[TurnColor.BLACK][0]
        if board.castling_rights[TurnColor.BLACK][1]:
            h ^= cls.castling_rights[TurnColor.BLACK][1]

        if board.possible_en_passant:
            h ^= cls.en_passant[board.possible_en_passant.algebraic[0]]

        if board.turn == TurnColor.BLACK:
            h ^= cls.black_turn

        return h

    # def __getitem__(self, item): # keep like this or change?
    #     """ gets the unique 64bit value of the piece on a position from the table
    #
    #     :param item: should contain a pieces.Piece instance
    #     :type item: pieces.Piece
    #
    #     :return: the unique 64bit value
    #     :rtype: int
    #     """
    #     piece = item
    #     i = self.pieces[f"{piece.color.name}_{piece.name.upper()}"]
    #     return self.table[i][piece.pos[0] + piece.pos[1] * 8]

    @classmethod
    def get_table_value(cls, piece_name, color, position):
        index = cls.pieces[f"{color.name}_{piece_name.upper()}"]
        return cls.table[index][position[0] + position[1] * 8]

    @classmethod
    def debug_values(cls, val):
        """ a debug method to view the table and compare a value in it

        :param val: the 64bit integer
        :type val: int
        """
        print("DEBUG HASHING VALUES")
        for i in cls.pieces.keys():
            print(i)
            values = cls.table[cls.pieces[i]]
            print("val in values")
            print(val in values)
            print(values)
            # 14061870981566557310

        print("castling rights")
        print(cls.castling_rights)

        print("en passant")
        print(cls.en_passant)

        print("black turn")
        print(cls.black_turn)

# board = loader.Board(fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", hasher = hasher)
# hash = hasher.hash(board)
#
# piece = board.board[6][4]
# print(piece.name, piece.pos)
# hash ^= hasher[piece, (4, 6)]
# hash ^= hasher[piece, (4, 4)]
# hash ^= hasher.black_turn
# hash ^= hasher.en_passant["e"]
#
# board.move("e2e4")
#
# print(hasher.hash(board) == hash)
