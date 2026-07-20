import random
import loader


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
    :type castling_rights: dict[str, list[int]]

    :var en_passant: holds the en passant values for the columns (aka. a->h)
    :type en_passant: dict[str, int]


    """
    rng = random.Random(0)

    pieces = {
            "white_pawn": 0,
            "white_knight": 1,
            "white_bishop": 2,
            "white_rook": 3,
            "white_queen": 4,
            "white_king": 5,
            "black_pawn": 6,
            "black_knight": 7,
            "black_bishop": 8,
            "black_rook": 9,
            "black_queen": 10,
            "black_king": 11,

        }

    table = [[bytes(0) for _ in range(64)] for _ in range(12)]
    black_turn = 0
    castling_rights = {}
    en_passant = {}

    def __init__(self):
        """ an initialization function that sets up all unique values in the attributes """
        used = set()
        for i in range(12):
            for j in range(64):
                # ensures that there are no repeats in teh hashing
                while True:
                    random_bits = self.rng.getrandbits(64)
                    if random_bits not in used:
                        used.add(random_bits)
                        self.table[i][j] = self.rng.getrandbits(64)
                        break

        self.black_turn = self.rng.getrandbits(64)

        self.castling_rights["white"] = [self.rng.getrandbits(64), self.rng.getrandbits(64)]
        self.castling_rights["black"] = [self.rng.getrandbits(64), self.rng.getrandbits(64)]

        for i in range(8):
            self.en_passant[chr(97 + i)] = self.rng.getrandbits(64)

    def hash(self, board):
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
                    i = self.pieces[f"{piece.color}_{piece.name.lower()}"]
                    h ^= self.table[i][piece.pos[0] + piece.pos[1] * 8]

        if board.castling_rights["white"][0]:
            h ^= self.castling_rights["white"][0]
        if board.castling_rights["white"][1]:
            h ^= self.castling_rights["white"][1]
        if board.castling_rights["black"][0]:
            h ^= self.castling_rights["black"][0]
        if board.castling_rights["black"][1]:
            h ^= self.castling_rights["black"][1]

        if board.possible_en_passant:
            h ^= self.en_passant[board.possible_en_passant.algebraic[0]]

        if board.turn == "black":
            h ^= self.black_turn

        return h

    def __getitem__(self, item): # keep like this or change?
        """ gets the unique 64bit value from the table

        :param item: should contain a pieces.Piece instance and a position.PositionVector2D instance
        :type item: tuple[pieces.Piece, position.PositionVector2D]

        :return: the unique 64bit value
        :rtype: int
        """
        piece, position = item
        i = self.pieces[f"{piece.color}_{piece.name.lower()}"]
        return self.table[i][position[0] + position[1] * 8]

    def debug_values(self, val):
        """ a debug method to view the table and compare a value in it

        :param val: the 64bit integer
        :type val: int
        """
        for i in self.pieces.keys():
            print(i)
            values = self.table[self.pieces[i]]
            print("val in values")
            print(val in values)
            print(self.table[self.pieces[i]])
            # 3237877843526964457

        print("castling rights")
        print(self.castling_rights)

        print("en passant")
        print(self.en_passant)


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
