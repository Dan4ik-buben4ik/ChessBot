import random
import loader


class ZobristHasher:
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

    def __getitem__(self, item):
        piece, position = item
        i = self.pieces[f"{piece.color}_{piece.name.lower()}"]
        return self.table[i][position[0] + position[1] * 8]

    def debug_values(self, val):
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
