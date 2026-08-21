from .util import *
from .error import *
from .move import Move
from .hashing import ZobristHasher

from dataclasses import dataclass



class Board:
    #slots later?
    pawns = 0
    knights = 0
    bishops = 0
    rooks = 0
    queens = 0
    kings = 0



    occupancy_color = [0, 0]
    occupancy = 0

    turn = WHITE

    castling_rights = 0
    ep_square: Square | None = None

    half_moves = 0
    full_moves = 1

    hash = 0

    history = []
    repetition_table = {}

    def piece_at(self, square):
        bit = 1 << square
        if bit & self.pawns:
            return PAWN
        if bit & self.knights:
            return KNIGHT
        if bit & self.bishops:
            return BISHOP
        if bit & self.rooks:
            return ROOK
        if bit & self.queens:
            return QUEEN
        if bit & self.kings:
            return KING
        return None


    def color_at(self, square):
        bit = 1 << square
        if bit & self.occupancy_color[WHITE]:
            return WHITE
        elif bit & self.occupancy_color[BLACK]:
            return BLACK
        else:
            return None

    def set_piece_at(self, square, piece_type, color):
        bit = 1 << square
        if piece_type == PAWN:
            self.pawns |= bit
        elif piece_type == KNIGHT:
            self.knights |= bit
        elif piece_type == BISHOP:
            self.bishops |= bit
        elif piece_type == ROOK:
            self.rooks |= bit
        elif piece_type == QUEEN:
            self.queens |= bit
        elif piece_type == KING:
            self.kings |= bit


        self.occupancy_color[color] |= bit
        self.occupancy |= bit
        self.hash ^= ZobristHasher.get_table_value(color, piece_type, square)
        return None

    def remove_piece_at(self, square):
        piece_type = self.piece_at(square)
        piece_color = self.color_at(square)
        bit = 1 << square
        if bit & self.pawns:
            self.pawns &= ~bit
        elif bit & self.knights:
            self.knights &= ~bit
        elif bit & self.bishops:
            self.bishops &= ~bit
        elif bit & self.rooks:
            self.rooks &= ~bit
        elif bit & self.queens:
            self.queens &= ~bit
        elif bit & self.kings:
            self.kings &= ~bit
        else:
            return None, None

        self.occupancy_color[piece_color] &= ~bit
        self.occupancy &= ~bit
        self.hash ^= ZobristHasher.get_table_value(piece_color, piece_type, square)
        return piece_type, piece_color


    def attacks_mask(self, square: Square):
        bb_square = 1 << square

        if bb_square & self.pawns:
            return BB_PAWN_ATTACKS[self.turn][square]
        elif bb_square & self.knights:
            return BB_KNIGHT_ATTACKS[square]
        elif bb_square & self.kings:
            return BB_KING_ATTACKS[square]
        else:
            raise NotImplementedError

    def is_en_passant(self, move):
        return (
            self.ep_square and
            move.to_square == self.ep_square and
            self.piece_at(move.from_square) == PAWN and
            self.piece_at(move.to_square) is None
        )

    def is_attacked(self, square):
        return NotImplementedError

    def push(self, move):
        """ assume the move is perfectly legal"""
        # update history
        self.history.append(_BitBoardState(self))

        # update en passant
        ep_square = self.ep_square
        if self.ep_square:
            self.hash ^= ZobristHasher.en_passant[self.ep_square % 8]
            self.ep_square = None

        piece, piece_color = self.remove_piece_at(move.from_square)
        captured_piece, captured_piece_color = self.remove_piece_at(move.to_square)

        #handle promotion
        if move.promotion:
            piece = move.promotion

        #handle castling
        if piece == KING and abs(move.to_square - move.from_square) == 2:
            if move.to_square > move.from_square:
                self.remove_piece_at(H1 if self.turn == WHITE else H8)
                self.set_piece_at(F1 if self.turn == WHITE else F8, ROOK, self.turn)
            else:
                self.remove_piece_at(A1 if self.turn == WHITE else A8)
                self.set_piece_at(D1 if self.turn == WHITE else D8, ROOK, self.turn)


        #handle pawn moves
        if piece == PAWN:
            diff = move.to_square - move.from_square

            if diff == 16 and square_rank(move.from_square) == RANK_2:
                self.ep_square = move.from_square + 8
                self.hash ^= ZobristHasher.en_passant[self.ep_square % 8]
            elif diff == -16 and square_rank(move.from_square) == RANK_7:
                self.ep_square = move.from_square - 8
                self.hash ^= ZobristHasher.en_passant[self.ep_square % 8]
            elif move.to_square == ep_square and abs(diff) in (7, 9) and not captured_piece:
                shift = -8 if self.turn == WHITE else 8
                self.remove_piece_at(move.to_square + shift)
                captured_piece = move.to_square + shift


        #update castling rights
        if piece == KING or piece == ROOK:
            castling_val = CASTLING_RIGHTS_UPDATE_BY_SQUARE.get(move.from_square, 0)
            self.castling_rights &= ~castling_val
            self.hash ^= ZobristHasher.castling_rights[castling_val]

        self.set_piece_at(move.to_square, piece, piece_color)



        # update the move clocks
        if piece == PAWN or captured_piece:
            self.half_moves = 0
        else:
            self.half_moves += 1

        if self.turn == BLACK:
            self.full_moves += 1


        # update the turn
        self.turn ^= 1

        self.hash ^= ZobristHasher.black_turn

        #update repetition table
        if self.repetition_table.get(self.hash):
            self.repetition_table[self.hash] += 1
        else:
            self.repetition_table[self.hash] = 1

        try:
            assert self.hash == ZobristHasher.hash(self)
        except AssertionError as err:
            print(self.hash)
            print(ZobristHasher.hash(self))
            ZobristHasher.debug(ZobristHasher.hash(self) ^ self.hash)
            self.construct()
            raise err



    def pop(self):
        if not self.history:
            return False
        prev_state = self.history.pop()
        prev_state.restore()
        return True

    def generate_pseudo_legal_moves(self):
        # generate non pawns moves
        non_pawns = self.occupancy_color[self.turn] & ~self.pawns
        for from_square in scan_forward_bb(non_pawns):
            moves = self.attacks_mask(from_square) & ~self.occupancy_color[self.turn]
            for to_square in scan_forward_bb(moves):
                yield Move(from_square, to_square)


        #generate pawns moves
        ally_pawns = self.pawns & self.occupancy_color[self.turn]
        if not ally_pawns:
            return

        #captures
        for from_square in scan_backward_bb(ally_pawns):
            targets = BB_PAWN_ATTACKS[self.turn][from_square] & self.occupancy_color[1 ^ self.turn]
            for to_square in scan_backward_bb(targets):
                if square_rank(to_square) in (RANK_1, RANK_8):
                    yield Move(from_square, to_square, KNIGHT)
                    yield Move(from_square, to_square, BISHOP)
                    yield Move(from_square, to_square, ROOK)
                    yield Move(from_square, to_square, QUEEN)
                else:
                    yield Move(from_square, to_square)

        #advances
        if self.turn == WHITE:
            single_moves = ally_pawns << 8 & ~self.occupancy
            double_moves = single_moves << 8 & ~self.occupancy & BB_RANK_4
        else:
            single_moves = ally_pawns >> 8 & ~self.occupancy
            double_moves = single_moves >> 8 & ~self.occupancy & BB_RANK_5

        for to_square in scan_backward_bb(single_moves):
            from_square = to_square + (-8 if self.turn == WHITE else 8)
            if square_rank(to_square) in (RANK_1, RANK_8):
                yield Move(from_square, to_square, KNIGHT)
                yield Move(from_square, to_square, BISHOP)
                yield Move(from_square, to_square, ROOK)
                yield Move(from_square, to_square, QUEEN)
            else:
                yield Move(from_square, to_square)

        for to_square in scan_backward_bb(double_moves):
            from_square = to_square + (-16 if self.turn == WHITE else 16)
            yield Move(from_square, to_square)

        #generate en passant
        if not self.ep_square or self.ep_square & self.occupancy:
            return

        capturers = ally_pawns & BB_PAWN_ATTACKS[1 ^ self.turn][self.ep_square] & (BB_RANK_4 if self.turn == WHITE else BB_RANK_5)
        for from_square in scan_backward_bb(capturers):
            yield Move(from_square, self.ep_square)

        # raise NotImplementedError

    @classmethod
    def from_fen(cls, fen: str):
        bit_board = cls()

        sections = fen.split(" ")

        for file_i, row in enumerate(sections[0].split("/")):
            empty = 0
            for piece in row:
                if piece.isnumeric():
                    empty += int(piece)
                else:
                    square = (7 - file_i) * 8 + empty
                    piece_colour = WHITE if piece.isupper() else BLACK
                    piece_type = PIECE_SYM.index(piece.lower())
                    bit_board.set_piece_at(square, piece_type, piece_colour)
                    empty += 1


        if sections[1] == "w":
            bit_board.turn = WHITE
        if sections[1] == "b":
            bit_board.turn = BLACK

        castles = sections[2]
        if "K" in castles:
            bit_board.castling_rights |= WHITE_KINGS_CASTLE
        if "Q" in castles:
            bit_board.castling_rights |= WHITE_QUEENS_CASTLE
        if "k" in castles:
            bit_board.castling_rights |= BLACK_KINGS_CASTLE
        if "q" in castles:
            bit_board.castling_rights |= BLACK_QUEENS_CASTLE

        bit_board.ep_square = SQUARE_NAMES.index(sections[3]) if sections[3] != "-" else None

        bit_board.half_moves = int(sections[4])
        bit_board.full_moves = int(sections[5])

        bit_board.hash = ZobristHasher.hash(bit_board)
        return bit_board


    def to_fen(self) -> str:
        fen = ""

        # --DEBUG--
        # print("\nFEN INPUT")
        # print(board.player)
        # print(board.kings_castle)
        # print(board.possible_en_passant)
        # print(board.half_moves, board.full_moves)
        # print()

        # Positions (section 1)
        for rank in range(7, -1, -1):
            empty = 0

            for file in range(8):
                square = rank * 8 + file
                piece, color = self.piece_at(square), self.color_at(square)

                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                    sym = PIECE_SYM[piece]
                    fen += sym.upper() if color == WHITE else sym.lower()
                    empty = 0

            if empty > 0:
                fen += str(empty)

            if rank != 0:
                fen += "/"

        if self.turn == WHITE:
            fen += " w"
        else:
            fen += " b"

        # Castling (sections 2 and 3)
        possible_castles = ""
        if self.castling_rights & WHITE_KINGS_CASTLE:
            possible_castles += "K"
        if self.castling_rights & WHITE_QUEENS_CASTLE:
            possible_castles += "Q"
        if self.castling_rights & BLACK_KINGS_CASTLE:
            possible_castles += "k"
        if self.castling_rights & BLACK_QUEENS_CASTLE:
            possible_castles += "q"

        fen += f" {possible_castles if possible_castles else '-'}"

        # en passant
        if self.ep_square is None:
            fen += " -"
        else:
            fen += f" {SQUARE_NAMES[self.ep_square]}"

        # half moves and full moves
        fen += f" {self.half_moves} {self.full_moves}"

        return fen

    def construct(self):
        # A function that prints the board. NOTHING TO BE CHANGED HERE
        print(f"{'           ' * 2}Black")
        print("|-----" * 8 + "|")
        for rank in range(7, -1, -1):
            for file in range(8):
                square = rank * 8 + file
                piece, color = self.piece_at(square), self.color_at(square)

                if piece is None:
                    val = " "
                else:
                    sym = PIECE_SYM[piece]
                    val = sym.upper() if color == WHITE else sym.lower()
                print(f"|  {val}  " if len(str(val)) == 1 else f"|  {val} ", end="")
            print("|", end="")
            print(f"  {rank}")
            print("|-----" * 8 + "|")
        # section to add letters
        print("   ", end="")
        # h - 104, a - 97
        for letter in range(97, 105):  # H -> A ~ (104, 96, -1)
            print(f"{chr(letter)}     ", end="")
        print(f"\n{'           ' * 2}White")
        print(f"\nFEN: {self.to_fen()}")



class _BitBoardState:
    __slots__ = (
        "pawns", "knights", "bishops", "rooks", "queens", "kings", "occupancy_color", "castling_rights",
        "ep_square", "half_moves", "full_moves", "hash",
    )

    def __init__(self, bitboard):
        # slots later?
        self.pawns = bitboard.pawns
        self.knights = bitboard.knights
        self.bishops = bitboard.bishops
        self.rooks = bitboard.rooks
        self.queens = bitboard.queens
        self.kings = bitboard.kings

        self.occupancy_color = bitboard.occupancy_color
        self.castling_rights = bitboard.castling_rights
        self.ep_square: Square | None = bitboard.ep_square
        self.half_moves = bitboard.half_moves
        self.full_moves = bitboard.full_moves
        self.hash = bitboard.hash

    def restore(self, bitboard):
        bitboard.pawns = self.pawns
        bitboard.knights = self.knights
        bitboard.bishops = self.bishops
        bitboard.rooks = self.rooks
        bitboard.queens = self.queens
        bitboard.kings = self.kings

        bitboard.occupancy_color = self.occupancy_color
        bitboard.castling_rights = self.castling_rights
        bitboard.ep_square = self.ep_square
        bitboard.half_moves = self.half_moves
        bitboard.full_moves = self.full_moves
        bitboard.hash = self.hash

        bitboard.occupancy = self.occupancy_color[WHITE] | self.occupancy_color[BLACK]
        bitboard.turn ^= 1

    def __repr__(self):
        return f"{self.hash}"
