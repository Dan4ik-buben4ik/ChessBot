from pieces import Piece, Rook, King, Pawn, Bishop, Queen, Knight
from position import PositionVector2D
from fen_converter import FEN_to_board, board_to_FEN
from hashing import ZobristHasher
from util import TurnColor, EvalTable
from Move import Move
from Errors import ImpossibleMoveException
import MoveGenerator

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
    """ the main class that contains the board with the pieces and the game information

    Attributes:

    :ivar debug: adds debug mode that prints stuff into the console
    :type debug: bool

    :var board: a 8x8 array filled with either 0's (empty squares) or pieces.Piece instances
    :type board: list[list[int | pieces.Piece]]

    :var turn: the current player color
    :type turn: util.TurnColor

    :var kings: kings position in the board
    :type kings: dict[util.TurnColor, pieces.Piece]

    :var castling_rights: a dictionary that holds the castling rights for both sides
    :type castling_rights: dict[str, [bool]]

    :var possible_en_passant: the final position of the pawn after the en passant
    :type possible_en_passant: position.PositionVector2D | None

    :var half_moves: the number total moves for white + black
    :type half_moves: int

    :var full_moves: the number of moves white had made
    :type full_moves: int

    :var hasher: the Zobrist hasher for the board, holding the 64bit data for the board hash
    :type hasher: hashing.ZobristHasher

    :var hash: the 64bit hash value for the board
    :type hash: int

    :var repetition_table: table with the hashes of the positions and the number of times it had appeared
    :type repetition_table: dict[int, int]

    :var history: a list with previous moves and game states
    :type history: list[loader.HistoryEntree]


    """
    def __init__(self, fen: str, *, debug=False):
        """ Initializes the class instance


        :param fen: the FEN string of the position
        :type fen: str

        :param debug:
        """
        self.debug = debug

        self.board = [[0 for _ in range(8)] for _ in range(8)]

        # establishes whose move it is currently
        self.turn = TurnColor.WHITE

        # stores king's position (useful for checks)
        # collapse in 1 dict?
        self.kings = {}
        self.castling_rights = {TurnColor.WHITE: [False, False], TurnColor.BLACK: [False, False]}  # king, queen side

        self.possible_en_passant: PositionVector2D | None = None

        self.half_moves = 0
        self.full_moves = 1

        FEN_to_board(fen, self)

        # this is the list of all positions sins last pawn movement/capture. Used for the triple-repetition-draw check
        self.hasher = ZobristHasher
        self.hash = self.hasher.hash(self)
        self.repetition_table = {self.hash: 1}

        self.history = []

    @property
    def is_endgame(self):
        white_material = 0
        black_material = 0
        queens = True
        for row in self.board:
            for piece in row:
                if piece == 0:
                    continue
                if piece.name != "Pawn" and piece.name != "King":
                    if piece.color == TurnColor.WHITE:
                        white_material += EvalTable.piece_value[piece.name]
                    else:
                        black_material += EvalTable.piece_value[piece.name]

                if piece.name == "Queen":
                    queens = True

        if queens:
            if black_material <= 1300 and white_material <= 1300:
                return True
        elif black_material <= 1600 and white_material <= 1600:
            return True

        return False

    @property
    def open_files(self):
        column = [True for _ in range(8)]
        for row_i in range(8):
            for column_i in range(8):
                piece = self.board[column_i][row_i]
                if piece == 0:
                    continue
                if piece.name == "Pawn":
                    column[row_i] = False
                    break

        return column

    def play(self, move: Move):
        if move in MoveGenerator.generate_legal_moves(self):
            self.push(move)
        else:
            raise ImpossibleMoveException

    def push(self, move: Move) -> None:

        # san_move_txt = uci_to_san(self, uci_move_txt)  # removes the en_passant pawn
        # if self.debug:
        #     print(f"san move: {san_move_txt}")
        #
        # init_pos, new_pos, promotion = uci_decoder(uci_move_txt)

        piece = self.board[move.init_pos[1]][move.init_pos[0]]

        self.board[piece.pos[1]][piece.pos[0]] = 0  # makes the old square empty
        self.hash ^= self.hasher.get_table_value(piece.name, piece.color, piece.pos)

        if move.promotion:
            if move.promotion == "q":
                piece = Queen(self, piece.color, move.final_pos)
            if move.promotion == "r":
                piece = Rook(self, piece.color, move.final_pos)
            elif move.promotion == "n":
                piece = Knight(self, piece.color, move.final_pos)
            elif move.promotion == "b":
                piece = Bishop(self, piece.color, move.final_pos)

            if self.debug:
                print(f"promoting to {piece.name} on {piece.pos.algebraic}")

        elif self._is_move_castle(piece, move):
            direction = PositionVector2D.sign(move.pos_change[0])
            rook = self.board[move.init_pos[1]][0 if direction == -1 else 7]
            self.board[rook.pos[1]][rook.pos[0]] = 0  # makes the old square empty
            self.hash ^= self.hasher.get_table_value(rook.name, rook.color, rook.pos)

            new_rook_pos = move.init_pos + (direction, 0)
            rook.pos = new_rook_pos

            self.board[new_rook_pos[1]][new_rook_pos[0]] = rook
            self.hash ^= self.hasher.get_table_value(rook.name, rook.color, rook.pos)

        elif self._is_move_en_passant(piece, move):
            captured_pos = move.final_pos - (0, piece.moving_direction)
            captured_piece = self.board[captured_pos[1]][captured_pos[0]]

            self.board[captured_pos[1]][captured_pos[0]] = 0
            self.hash ^= self.hasher.get_table_value(captured_piece.name, captured_piece.color, captured_piece.pos)

        # checks if the new space is occupied and performs a needed hash operations
        captured_piece = self.board[move.final_pos[1]][move.final_pos[0]]
        if captured_piece != 0:
            self.hash ^= self.hasher.get_table_value(captured_piece.name, captured_piece.color, captured_piece.pos)

        # update the table and its hash
        piece.pos = move.final_pos
        self.board[move.final_pos[1]][move.final_pos[0]] = piece
        self.hash ^= self.hasher.get_table_value(piece.name, piece.color, piece.pos)

        if self.debug:
            print(f"Moved {piece.name} from {move.init_pos.algebraic} to {move.final_pos.algebraic}")

        self.history.append(HistoryEntree(move, captured_piece, self.possible_en_passant, self.castling_rights, self.half_moves, self.full_moves, self.hash))

        # update the game state
        self.update_game_state()  # should be before or after push?
        self.update_castling_rights(piece, move)
        self.update_en_passant(piece, move)
        self.update_move_clock(piece, captured_piece)
        self.switch_turn()

    # ===========================================================================================================================
    # ===========================================================================================================================
    # ===========================================================================================================================

    def _is_move_castle(self, piece, move):
        if piece.name == "King" and abs(move.pos_change)[0] == 2:
            return True
        return False

    def _is_move_en_passant(self, piece, move):
        if piece.name == "Pawn" and abs(move.pos_change)[0] == 1 and move.final_pos == self.possible_en_passant:
            return True
        return False

    def is_move_capture(self, move):
        piece = self.board[move.init_pos[1]][move.init_pos[0]]
        return self.board[move.final_pos[1]][move.final_pos[0]] != 0 or self._is_move_en_passant(piece, move)

    def is_move_check(self, move):
        self.push(move)
        check, attackers = self.check_if_king_attacked(self.turn)
        self.pop()
        return check

    def update_castling_rights(self, piece, move) -> None:
        if isinstance(piece, King):
            if self.castling_rights[self.turn] != [False, False]:
                self.castling_rights[self.turn] = [False, False]
                self.hash ^= self.hasher.castling_rights[self.turn][0]
                self.hash ^= self.hasher.castling_rights[self.turn][1]

        elif isinstance(piece, Rook):
            if move.init_pos.algebraic[0] == "a" and self.castling_rights[self.turn][0] is True:
                self.castling_rights[self.turn][0] = False
                self.hash ^= self.hasher.castling_rights[self.turn][0]
            elif move.init_pos.algebraic[0] == "h" and self.castling_rights[self.turn][1] is True:
                self.castling_rights[self.turn][1] = False
                self.hash ^= self.hasher.castling_rights[self.turn][1]

        if self.check_if_king_attacked(self.turn)[0] is True:
            opponent_color = self.turn.next()
            if self.castling_rights[opponent_color] != [False, False]:
                self.castling_rights[opponent_color] = [False, False]
                self.hash ^= self.hasher.castling_rights[opponent_color][0]
                self.hash ^= self.hasher.castling_rights[opponent_color][1]

    def update_en_passant(self, piece, move) -> None:
        if self.possible_en_passant:
            self.hash ^= self.hasher.en_passant[self.possible_en_passant.algebraic[0]]
            self.possible_en_passant = None

        if not isinstance(piece, Pawn):
            return

        if (move.final_pos - move.init_pos)[1] == piece.moving_direction * 2:
            self.possible_en_passant = move.init_pos + (0, piece.moving_direction)
            self.hash ^= self.hasher.en_passant[self.possible_en_passant.algebraic[0]]

    def update_move_clock(self, piece, captured_piece):
        self.half_moves += 1
        if isinstance(piece, Pawn) or captured_piece != 0:
            self.half_moves = 0

        if self.turn == TurnColor.BLACK:
            self.full_moves += 1

    def switch_turn(self):
        # changes the current player, aka the turn
        self.hash ^= self.hasher.black_turn
        self.turn = self.turn.next()

    def update_game_state(self):
        if self.repetition_table.get(self.hash):
            self.repetition_table[self.hash] += 1
        else:
            self.repetition_table[self.hash] = 1

    def pop(self):
        """removes last move"""
        history: HistoryEntree = self.history.pop()
        self.possible_en_passant = history.previous_en_passant
        self.castling_rights = history.previous_castling_rights
        self.half_moves = history.previous_half_moves
        self.full_moves = history.previous_full_moves
        self.hash = history.previous_hash
        self.turn = self.turn.previous()

        # self.move = move
        # self.captured_piece = captured_piece
        move = history.move
        piece = self.board[move.final_pos[1]][move.final_pos[0]]
        self.board[move.final_pos[1]][move.final_pos[0]] = 0

        # bringing back the captured piece
        captured_piece = history.captured_piece
        if captured_piece != 0:
            self.board[captured_piece.pos[1]][captured_piece.pos[0]] = captured_piece

        if move.promotion:
            piece = Pawn(self, piece.color, move.init_pos, debug=self.debug)

        if self._is_move_castle(piece, move):
            direction = PositionVector2D.sign(move.pos_change[0])
            new_rook_pos = move.init_pos + (direction, 0)
            rook_init_pos = PositionVector2D((move.init_pos[1], 0 if direction == -1 else 7))

            rook = self.board[new_rook_pos[1]][new_rook_pos[0]]
            self.board[new_rook_pos[1]][new_rook_pos[0]] = 0

            self.board[move.init_pos[1]][0 if direction == -1 else 7] = rook
            rook.pos = rook_init_pos

        piece.pos = move.init_pos
        self.board[move.init_pos[1]][move.init_pos[0]] = piece

    def check_if_king_attacked(self, color):
        king = self.kings[color]
        res, positions_that_attack_king = self.check_if_pos_attacked(king.pos, self.turn)
        return res, positions_that_attack_king

    def check_if_pos_attacked(self, pos: PositionVector2D | tuple[int, int], turn_color: TurnColor) -> tuple[bool, list]:
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
                    if isinstance(piece, (Rook, Queen)) and sum(abs(direction).position) == 1:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    elif isinstance(piece, (Bishop, Queen)) and sum(abs(direction).position) == 2:
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

    def _knights_attacking_pos(self, pos: PositionVector2D, turn_color: TurnColor) -> GeneratorType:
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

    def game_end_check(self):
        # returns: game_finished (True if yes and False if not), winner (str of the player or None if draw)
        if not len(list(MoveGenerator.generate_legal_moves(self))) == 0:
            # check if triple move draw or 50 move draw
            if self.repetition_table.get(self.hash):
                if self.repetition_table.get(self.hash) >= 3:
                    return True, None
            elif self.half_moves >= 100:
                return True, None
            else:
                return False, None

        opponent_color = self.turn.next()
        if self.check_if_king_attacked(opponent_color)[0]:
            return True, opponent_color
        else:
            return False, None

    def to_fen(self):
        return board_to_FEN(self)

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


class HistoryEntree:
    def __init__(self, move, captured_piece, previous_en_passant: PositionVector2D, previous_castling_rights, previous_half_moves, previous_full_moves, previous_hash):
        self.move = move
        self.captured_piece = captured_piece
        self.previous_en_passant = previous_en_passant
        self.previous_castling_rights = previous_castling_rights
        self.previous_half_moves = previous_half_moves
        self.previous_full_moves = previous_full_moves
        self.previous_hash = previous_hash
