from pieces import Piece, Rook, King, Pawn, Bishop, Queen, Knight
from Errors import UnrecognisableMove, PieceColorException, ImpossibleMoveException, UnderCheckException, JustError
from position import PositionVector2D
from fen_converter import FEN_to_board, board_to_FEN
from Move import uci_to_san, san_to_uci, uci_encoder, uci_decoder

from types import GeneratorType



# board check logic
# if (pos_change[0] != 0 and pos_change[1] != 0) or not (8 > new_pos[0] > -1 and 8 > new_pos[1] > -1):
#     raise ImpossibleMoveException(self, f"{self.name} can't reach", self.pos, new_pos)
#
# # Checks if the piece is actually moving
# elif pos_change[0] == 0 and pos_change[1] == 0:
#     raise ImpossibleMoveException(self, "Need to move", self.pos, new_pos)


# King- K
# Queen - Q --
# Rook - R --
# Knight - N --
# Bishop - B --
# Pawn - P or non --

# Board Visualisation (with position on the side and coordinates in the squares)
#                       White
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,0 | 1,0 | 2,0 | 3,0 | 4,0 | 5,0 | 6,0 | 7,0 |  8
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,1 | 1,1 | 2,1 | 3,1 | 4,1 | 5,1 | 6,1 | 7,1 |  7
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,2 | 1,2 | 2,2 | 3,2 | 4,2 | 5,2 | 6,2 | 7,2 |  6
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,3 | 1,3 | 2,3 | 3,3 | 4,3 | 5,3 | 6,3 | 7,3 |  5
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,4 | 1,4 | 2,4 | 3,4 | 4,4 | 5,4 | 6,4 | 7,4 |  4
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,5 | 1,5 | 2,5 | 3,5 | 4,5 | 5,5 | 6,5 | 7,5 |  3
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,6 | 1,6 | 2,6 | 3,6 | 4,6 | 5,6 | 6,6 | 7,6 |  2
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,7 | 1,7 | 2,7 | 3,7 | 4,7 | 5,7 | 6,7 | 7,7 |  1
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#         a     b     c     d     e     f     g     h


# Board Visualisation (with coordinate system on the axis and positions in the squares)  ~ swap A and H
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
#  7   | A1  | B1  | C1  | D1  | E1  | F1  | G1  | H1  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|

class Board:
    def __init__(self, fen: str, hasher, *, debug=False):
        self.debug = debug

        self.board = [[0 for _ in range(8)] for _ in range(8)]

        # establishes whose move it is currently
        self.turn = "white"  # "white"

        # stores king's position (useful for checks)
        # collapse in 1 dict?
        self.kings = {}
        self.castling_rights = {"white": [False, False], "black": [False, False]}  # king, queen side

        # check
        self.check = False
        self.positions_that_attack_king = []

        self.possible_en_passant: PositionVector2D | None = None

        self.possible_moves = []
        self.half_moves = 0
        self.full_moves = 1

        FEN_to_board(fen, self)

        # this is the list of all positions sins last pawn movement/capture. Used for the triple-repetition-draw check
        self.hasher = hasher
        self.hash = hasher.hash(self)
        self.repetition_table = {self.hash: 1}

    # ===========================================================================================================================
    # ===========================================================================================================================
    # ===========================================================================================================================

    def move(self, uci_move_txt: str) -> None:  # maybe get the init_pos and new_pos as an input?
        # break down into smaller functions like check, castle
        san_move_txt = uci_to_san(self, uci_move_txt)  # removes the en_passant pawn
        if self.debug:
            print(f"san move: {san_move_txt}")

        # getting the piece
        init_pos, new_pos, promotion = uci_decoder(uci_move_txt)
        # identifier that helps to see methods
        piece = self.board[init_pos[1]][init_pos[0]]



        # updates the position of the piece
        self.push(uci_move_txt)

        self.update_game_state()  # should be before or after push?
        self.update_castling_rights(piece, init_pos)
        self.update_en_passant(piece, init_pos, new_pos)
        self.update_move_clock(piece, san_move_txt)
        self.switch_turn()

        # print(board_to_FEN(self))
        # target = self.hasher.hash(self)
        # print(f"target {target}")
        #
        # print(self.hash)
        # diff = self.hash ^ target
        # print(diff)
        # self.hasher.debug_values(diff)

        assert self.hash == self.hasher.hash(self)

    def _is_castle(self, piece, init_pos, new_pos):
        if piece.name == "King" and abs(new_pos-init_pos)[0] == 2:
            return True
        return False

    def _is_en_passant(self, piece, init_pos, new_pos):
        if piece.name == "Pawn" and abs(new_pos - init_pos)[0] == 1 and new_pos == self.possible_en_passant:
            return True
        return False




# ===========================================================================================================================
# ===========================================================================================================================
# ===========================================================================================================================
    def push(self, uci_move_txt: str) -> None:  # TODO: make the input a move instance
        # A function that updates the pieces position on the board
        init_pos, new_pos, promotion = uci_decoder(uci_move_txt)
        # work for the en passant pawn capture and the castling
        piece = self.board[init_pos[1]][init_pos[0]]

        self.board[piece.pos[1]][piece.pos[0]] = 0  # makes the old square empty
        self.hash ^= self.hasher[piece, piece.pos]

        if promotion:
            if promotion == "Q":
                piece = Queen(self, piece.color, new_pos)
            if promotion.upper() == "R":
                piece = Rook(self, piece.color, new_pos)
            elif promotion == "N":
                piece = Knight(self, piece.color, new_pos)
            elif promotion == "B":
                piece = Bishop(self, piece.color, new_pos)


            if self.debug:
                print(f"promoting to {piece.name} on {piece.pos.algebraic}")

        elif self._is_castle(piece, init_pos, new_pos):
            #TODO: rewrite to suit the Move class
            direction = PositionVector2D.sign((new_pos - init_pos)[0])
            rook_pos = PositionVector2D((0 if direction == -1 else 7, new_pos[1]))
            new_rook_pos = init_pos + (direction, 0)
            rook_move = f"{rook_pos.algebraic}{new_rook_pos.algebraic}"
            self.push(rook_move)

        elif self._is_en_passant(piece, init_pos, new_pos):
            # TODO: capture logic to standard
            captured_pos = new_pos - (0, piece.moving_direction)
            captured_piece = self.board[captured_pos[1]][captured_pos[0]]

            self.board[captured_pos[1]][captured_pos[0]] = 0
            self.hash ^= self.hasher[captured_piece, captured_pos]

        # checks if the new space is occupied and performs a needed hash operations
        captured_piece = self.board[new_pos[1]][new_pos[0]]
        if captured_piece != 0:
            self.hash ^= self.hasher[captured_piece, new_pos]

        # update the table and its hash
        piece.pos = new_pos
        self.board[new_pos[1]][new_pos[0]] = piece
        self.hash ^= self.hasher[piece, piece.pos]

        if self.debug:
            print(f"Moved {piece.name} from {init_pos.algebraic} to {new_pos.algebraic}")

    # ===========================================================================================================================
    # ===========================================================================================================================
    # ===========================================================================================================================

    def update_castling_rights(self, piece, old_pos) -> None:
        if isinstance(piece, King):
            if self.castling_rights[self.turn] != [False, False]:
                self.castling_rights[self.turn] = [False, False]
                self.hash ^= self.hasher.castling_rights[self.turn][0]
                self.hash ^= self.hasher.castling_rights[self.turn][1]

        elif isinstance(piece, Rook):
            if old_pos.algebraic[0] == "a" and self.castling_rights[self.turn][0] is True:
                self.castling_rights[self.turn][0] = False
                self.hash ^= self.hasher.castling_rights[self.turn][0]
            elif old_pos.algebraic[0] == "h" and self.castling_rights[self.turn][1] is True:
                self.castling_rights[self.turn][1] = False
                self.hash ^= self.hasher.castling_rights[self.turn][1]

        if self.check_if_king_attacked(self.turn)[0] is True:
            opponent_color = "white" if self.turn == "black" else "black"
            if self.castling_rights[opponent_color] != [False, False]:
                self.castling_rights[opponent_color] = [False, False]
                self.hash ^= self.hasher.castling_rights[opponent_color][0]
                self.hash ^= self.hasher.castling_rights[opponent_color][1]

    def update_en_passant(self, piece, old_pos, new_pos) -> None:
        if self.possible_en_passant:
            self.hash ^= self.hasher.en_passant[self.possible_en_passant.algebraic[0]]
            self.possible_en_passant = None

        if not isinstance(piece, Pawn):
            return

        if (new_pos - old_pos)[1] == piece.moving_direction * 2:
            self.possible_en_passant = old_pos + (0, piece.moving_direction)
            self.hash ^= self.hasher.en_passant[self.possible_en_passant.algebraic[0]]

    def update_move_clock(self, piece, san_move_txt):
        # TODO: get rid of the move txt. Shouldn't be
        self.half_moves += 1
        if isinstance(piece, Pawn) or "x" in san_move_txt:
            self.half_moves = 0

        if self.turn == "black":
            self.full_moves += 1

    def switch_turn(self):
        # changes the current player, aka the turn
        self.hash ^= self.hasher.black_turn
        if self.turn == "white":
            self.turn = "black"
        else:
            self.turn = "white"

    def update_game_state(self):
        if self.repetition_table.get(self.hash):
            self.repetition_table[self.hash] += 1
        else:
            self.repetition_table[self.hash] = 1

    def check_if_king_attacked(self, color):
        king = self.kings[color]
        res, positions_that_attack_king = self.check_if_pos_attacked(king.pos, self.turn)
        self.positions_that_attack_king = positions_that_attack_king
        return res, positions_that_attack_king

    def check_if_pos_attacked(self, pos: PositionVector2D | tuple[int, int], turn_color: str) -> tuple[bool, list]:
        directions_list = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        directions_list = list(map(lambda x: PositionVector2D(x), directions_list))
        direction_del = []
        pos_that_attack = []

        # check for knight
        pos_that_attack.extend(list(self._knights_attacking_pos(pos, turn_color)))

        # check for any other pieces
        for i in range(1, 8):
            for direction in directions_list:
                piece_pos = pos + direction * i
                if not (0 <= piece_pos[0] <= 7 and 0 <= piece_pos[1] <= 7):
                    direction_del.append(direction)
                    continue

                try:  # second - just in case - check
                    piece = self.board[piece_pos[1]][piece_pos[0]]
                except IndexError:
                    direction_del.append(direction)
                    continue

                if piece == 0 or piece == self:
                    pass
                elif piece.color == turn_color:
                    direction_del.append(direction)

                else:
                    if isinstance(piece, (Rook, Queen)) and sum(abs(direction)) == 1:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    elif isinstance(piece, (Bishop, Queen)) and sum(abs(direction)) == 2:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    elif isinstance(piece, Pawn) and i == 1:  # piece.direction somewhere
                        if (direction[0], direction[1]) in ((-1, -piece.moving_direction), (1, -piece.moving_direction)):
                            pos_that_attack.append(piece_pos)

                    elif isinstance(piece, King) and i == 1:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    direction_del.append(direction)

            for d in direction_del:
                directions_list.remove(d)
            direction_del = []

        return True if len(pos_that_attack) > 0 else False, pos_that_attack

    def _knights_attacking_pos(self, pos: PositionVector2D, turn_color: str) -> GeneratorType:
        knight_directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (-2, -1), (2, -1)]

        for i in knight_directions:
            knight_pos = pos + i
            if not (0 <= knight_pos[0] <= 7 and 0 <= knight_pos[1] <= 7):
                continue
            try:
                piece: Piece | 0 = self.board[knight_pos[1]][knight_pos[0]]
            except IndexError:
                continue

            if piece == 0:
                continue
            elif piece.name == "Knight" and piece.color != turn_color:
                yield knight_pos


    def game_end_check(self, move_generator):
        # returns: game_finished (True if yes and False if not), winner (str of the player or None if draw)
        if not len(list(move_generator.get_all_possible_moves(self))) == 0:
            # check if triple move draw or 50 move draw
            if self.repetition_table.get(board_to_FEN(self)[:-4]):
                if self.repetition_table.get(board_to_FEN(self)[:-4]) >= 3:
                    return True, None
            elif self.half_moves >= 100:
                return True, None
            else:
                return False, None

        opponent_color = "white" if self.turn == "black" else "black"
        if self.check_if_king_attacked(opponent_color)[0]:
            return True, opponent_color
        else:
            return False, None

    def construct(self):
        # A function that prints the board. NOTHING TO BE CHANGED HERE
        print(f"{'           ' * 2}Black")
        num = 8  # h - 104, a - 97
        print("|-----" * 8 + "|")
        for num_y, row in enumerate(self.board):
            for num_x, val in enumerate(row):
                if val == 0:
                    val = " "
                else:
                    val = val.sym
                print(f"|  {val}  " if len(str(val)) == 1 else f"|  {val} ", end="")
            print("|", end="")
            print(f"  {num}")
            num -= 1
            print("|-----" * 8 + "|")

        # section to add letters
        print("   ", end="")
        # h - 104, a - 97
        for letter in range(97, 105):  # H -> A ~ (104, 96, -1)
            print(f"{chr(letter)}     ", end="")
        print(f"\n{'           ' * 2}White")
        print(f"\nFEN: {board_to_FEN(self)}")


