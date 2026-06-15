try:
    from pieces import Piece, Rook, King, Pawn
except ImportError:
    from pieces import Piece, Rook, King
    # testing = True
    # class Knight(Piece):
    #     pass
    # class Pawn(Piece):
    #     pass
    # class Queen(Piece):
    #     pass
    # class Bishop(Piece):
    #     pass

from Errors import UnrecognisableMove, PieceColorException, ImpossibleMoveException, UnderCheckException, JustError
from position import PositionVector2D
from encoder import FEN_to_board, board_to_FEN


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
#      | 0,0 | 1,0 | 2,0 | 3,0 | 4,0 | 5,0 | 6,0 | 7,0 |  1
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,1 | 1,1 | 2,1 | 3,1 | 4,1 | 5,1 | 6,1 | 7,1 |  2
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,2 | 1,2 | 2,2 | 3,2 | 4,2 | 5,2 | 6,2 | 7,2 |  3
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,3 | 1,3 | 2,3 | 3,3 | 4,3 | 5,3 | 6,3 | 7,3 |  4
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,4 | 1,4 | 2,4 | 3,4 | 4,4 | 5,4 | 6,4 | 7,4 |  5
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,5 | 1,5 | 2,5 | 3,5 | 4,5 | 5,5 | 6,5 | 7,5 |  6
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,6 | 1,6 | 2,6 | 3,6 | 4,6 | 5,6 | 6,6 | 7,6 |  7
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#      | 0,7 | 1,7 | 2,7 | 3,7 | 4,7 | 5,7 | 6,7 | 7,7 |  8
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#         h     g     f     e     d     c     b     a


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
    def __init__(self, *, fen: str | bool = False, testing=False):
        # Create a 2d array with empty (0) squares
        # self.board: list
        # self.player: str
        # self.kings_pos: dict
        # self.kings_castle: dict

        self.board = [[0 for _ in range(8)] for _ in range(8)]

        # establishes whose move it is currently
        self.player = "white"  # "white"

        # stores king's position (useful for checks)
        # collapse in 1 dict?
        self.kings_pos = {"white": PositionVector2D((4, 7)), "black": PositionVector2D((4, 0))}
        self.kings_castle = {"white": [True, True], "black": [True, True]}  # king, queen side

        if fen:
            FEN_to_board(fen, self)

        # check
        self.check = False
        self.positions_that_attack_king = []

        self.possible_en_passant = None

        self.possible_moves = []
        self.half_moves = 0
        self.full_moves = 1


    @staticmethod
    def is_reachable_move(piece, init_pos, new_pos) -> None:

        # checks if the move is within the board
        if (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
            raise ImpossibleMoveException(piece, "Piece can't reach", init_pos, new_pos)

        # Checks if the piece is actually moving
        if init_pos == new_pos:
            raise ImpossibleMoveException(piece, "Piece doesn't move", init_pos, new_pos)

    # ===========================================================================================================================
    # ===========================================================================================================================
    # ===========================================================================================================================

    def move(self, uci_move_txt: str) -> None:
        # break down into smaller functions like check, castle
        san_move_txt = self.uci_to_san(uci_move_txt)

        # getting the piece
        piece, init_pos, new_pos, promotion = self.uci_decoder(uci_move_txt)

        # checks the symbol and colour of the piece
        if piece == 0:  # if the square is empty, raises error
            raise UnrecognisableMove(san_move_txt)
        elif piece.color != self.player:  # if the pieces colour is not of the current players turn, raises error
            raise PieceColorException(piece)

        # identifier that helps to see methods
        piece: Piece

        # print("Possible moves")
        # # print(list(piece.get_possible_moves()))
        # self.get_all_possible_moves()

        # check if currently under check
        print(f"The king is under check: {self.check}")
        if self.check:
            self.move_under_check(piece, init_pos, new_pos)
        # checks if castle
        elif self.check_if_castle(piece, init_pos, new_pos):
            self.castle(piece, init_pos, new_pos)
        else:  # maybe get the normal move check out?
            self.normal_move_check(piece, init_pos, new_pos)

        if isinstance(piece, Pawn):
            if promotion and not new_pos[1] in (0, 7):
                raise ImpossibleMoveException(piece, "Cant promote if not on the back rank", init_pos, new_pos)
            elif new_pos[1] in (0, 7) and not promotion:  # TODO: scrape when fixed input
                promotion = input("What piece are you promoting to? (capitalized first letter of piece): ")

        elif isinstance(piece, King):
            self.kings_castle[self.player] = [False, False]

        elif isinstance(piece, Rook):
            if init_pos.cord[0] == "a" and self.kings_castle[self.player][0] is True:
                self.kings_castle[self.player][0] = False
            elif init_pos.cord[0] == "h" and self.kings_castle[self.player][1] is True:
                self.kings_castle[self.player][1] = False

        # updates the position of the piece
        self.update_pos(piece, new_pos, promotion)

        # maybe bring into self.check_if_king_attacked ("colour")
        opponent_king_pos = self.kings_pos["black" if self.player == "white" else "white"]
        opponent_king: King = self.board[opponent_king_pos[1]][opponent_king_pos[0]]

        if self.check_if_king_attacked(opponent_king) is True:
            self.check = True
            print(f"check on the king, by {self.positions_that_attack_king}")
            # opponent_king.update_blocked_list(opponent_king.pos)

        # changes the current player, aka the turn
        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"

# ===========================================================================================================================
# ===========================================================================================================================
# ===========================================================================================================================
    def update_pos(self, piece: Piece, cord: PositionVector2D|tuple[int, int], promotion:None|str=None) -> None:  # !!!
        self.last_move = (piece, piece.pos, cord)
        # A function that updates the pieces position on the board
        self.board[piece.pos[1]][piece.pos[0]] = 0  # makes the old square empty
        if promotion and isinstance(piece, Pawn):
            # if promotion == "Q":
            #     self.board[cord[1]][cord[0]] = Queen(self, piece.color, cord)
            if promotion.upper() == "R":
                piece = Rook(self, piece.color, cord)
            # elif promotion == "N":
            #     piece = Knight(self, piece.color, cord)
            # elif promotion == "B":
            #     piece = Bishop(self, piece.color, cord)

        self.board[cord[1]][cord[0]] = piece  # puts the pieces symbol on the new spot
        piece.move(cord)

        if isinstance(piece, King):
            self.kings_pos[piece.color] = cord

    def normal_move_check(self, piece, init_pos, new_pos) -> None:
        # check if it is on the board
        self.is_reachable_move(piece, init_pos, new_pos)

        # piece class checks
        reach, reason = piece.reach_check(new_pos)
        if not reach:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)
        blocking, reason = piece.blocking_check(new_pos)
        if blocking:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)

    def check_if_king_attacked(self, king: King) -> bool:
        res, positions_that_attack_king = king.check_if_pos_attacked(king.pos)
        self.positions_that_attack_king = positions_that_attack_king
        return res

    def move_under_check(self, piece, init_pos, new_pos) -> None:
        print("Move Under Check")
        if isinstance(piece, King):
            self.normal_move_check(piece, init_pos, new_pos)
            return

        king_pos = self.kings_pos[self.player]
        king = self.board[king_pos[1]][king_pos[0]]

        if len(self.positions_that_attack_king) > 1:
            raise ImpossibleMoveException(piece, "Cannot move piece while the king is under check by 2+ pieces", init_pos, new_pos)

        # here begins the real check
        attacking_piece_pos = self.positions_that_attack_king[0]
        attacking_piece: Piece = self.board[attacking_piece_pos[1]][attacking_piece_pos[0]]
        # TODO: add back when implemented the knight back
        # if isinstance(attacking_piece, Knight) and new_pos != attacking_piece_pos:
        #     raise ImpossibleMoveException(piece, "Cannot block the knight checking the king", init_pos, new_pos)

        pos_change = king_pos - attacking_piece_pos
        # might yield an error
        #TODO: resolve a possible error
        attacking_line = attacking_piece.get_line_positions_towards_king(king_pos)[:pos_change+1]
        print(f"Attacking_line: {attacking_line}")
        if new_pos not in attacking_line:
            raise ImpossibleMoveException(piece, "Cannot move piece while the king is under check", init_pos, new_pos)

        self.normal_move_check(piece, init_pos, new_pos)

    def castle(self, piece, init_pos, new_pos) -> None:
        pos_change = new_pos - init_pos
        direction = PositionVector2D.sign(pos_change[0])
        # +pos = right | -pos = left

        if self.kings_castle[self.player][1 if direction > 0 else 0] is False:
            raise ImpossibleMoveException(piece, "The king/rook had already moved", init_pos, new_pos)

        king: King = piece
        can_castle, reason = king.castle(new_pos, direction)
        if can_castle is False:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)

        rook_pos = 0 if direction == -1 else 7, new_pos[1]
        print(f"rook pos in board.castle(): {rook_pos}")
        rook: Rook = self.board[rook_pos[1]][rook_pos[0]]

        rook_new_pos = (rook_pos[0] -2 if direction == 1 else rook_pos[0] + 3), rook_pos[1]

        self.update_pos(rook, rook_new_pos)

    def check_if_castle(self, piece: Piece, new_pos, init_pos) -> bool:
        # checks if castle
        if isinstance(piece, King) and self.kings_castle[self.player] == [True, True]:
            print("checked king in board.move()")
            pos_change = new_pos - init_pos
            if abs(pos_change[0]) == 2 and pos_change[1] == 0:
                if self.check is True:
                    raise ImpossibleMoveException(piece, f"attacking on {self.kings_pos[self.player]} is under check",
                                                  init_pos, new_pos)

                print("king is castling...")
                return True
        return False

    #TODO: Change the function behaviour when under check
    def get_all_possible_moves(self):
        self.possible_moves = []
        for row in self.board:
            for piece in row:
                if piece != 0:
                    piece: Piece
                    if piece.color == self.player:
                        moves = piece.get_possible_moves()
                        self.possible_moves.extend(moves)

        # do the union thingy
        if self.check:
            king_pos = self.kings_pos[self.player]
            king: King = self.board[king_pos[1]][king_pos[0]]
            temp_moves = {}
            temp_moves.update(king.get_possible_moves())
            if len(self.positions_that_attack_king) == 1:
                attacking_piece_pos = self.positions_that_attack_king[0]
                attacking_piece: Piece = self.board[attacking_piece_pos[1]][attacking_piece_pos[0]]
                pos_change = king_pos - attacking_piece_pos
                attacking_line = attacking_piece.get_line_positions_towards_king(king_pos)[:pos_change + 1]
                for sym in ("Q", "R", "B", "N", "P"):
                    temp_moves.add("".join((sym, )))


        print(self.possible_moves)


    def find_san_pieces(self, symbol: str, new_pos: PositionVector2D):
        result_pieces = []
        for row in self.board:
            for piece in row:
                if piece == 0:
                    continue
                elif piece.sym.upper() != symbol.upper():
                    continue
                elif piece.color != self.player:
                    continue

                piece: Piece
                if piece.reach_check(new_pos)[0] and not piece.blocking_check(new_pos)[0]:
                    result_pieces.append(piece)
        return result_pieces


    def uci_to_san(self, move):
        # eg. e2e4 -> e4 or g1f3 -> Nf3 or e7e8q -> e8=Q or a1d1 -> Ra1d1
        # TODO: need testing of pawn promotion and of 3 queen situation
        init_pos = PositionVector2D(move[:2])
        new_pos = PositionVector2D(move[2:4])
        try:
            promotion = move[4]
        except IndexError:
            promotion = None

        piece = self.board[init_pos[1]][init_pos[0]]
        possible_pieces: list[Piece] = self.find_san_pieces(piece.sym, new_pos)

        if len(possible_pieces) == 1:
            return f"{piece.sym.capitalize()}{new_pos.cord}{promotion if promotion else ''}"

        possible_prefix = []
        for cord in possible_pieces:
            if cord.pos == init_pos:
                continue
            possible_prefix.extend((cord.pos.cord[0], cord.pos.cord[1]))

        prefix = ""
        if init_pos.cord[1] in possible_prefix:
            prefix = prefix + init_pos.cord[0]
        if init_pos.cord[0] in possible_prefix:
            prefix = prefix + init_pos.cord[1]

        return f"{piece.sym.capitalize()}{prefix}{new_pos.cord}{promotion if promotion else ''}"

    def san_to_uci(self, move):
        #TODO: test with promotion and 3 queens
        if move[0] not in ("Q", "K", "R", "N", "B", "P"):
            move = "".join(("P", move))

        try:
            move, promotion = move.split("=")
        except ValueError:
            promotion = None

        piece_sym = move[0]
        new_pos = PositionVector2D(move[-2:])

        # logic to get the initial position
        possible_pieces = self.find_san_pieces(piece_sym, new_pos)

        if len(possible_pieces) == 1:
            return f"{possible_pieces[0].pos.cord}{new_pos.cord}{promotion if promotion else ''}"

        # finding prefix
        if len(move) == 5:
            return f"{move[1:3]}{new_pos.cord}{promotion if promotion else ''}"
        elif len(move) == 4:
            prefix = move[1]
        else:
            raise JustError

        for piece in possible_pieces:
            if prefix in piece.pos.cord:
                init_pos = piece.pos

        return f"{init_pos.cord}{new_pos.cord}{promotion if promotion else ''}"

    def uci_decoder(self, move):
        init_pos = PositionVector2D(move[:2])
        new_pos = PositionVector2D(move[2:4])

        piece = self.board[init_pos[1]][init_pos[0]]

        try:
            promotion = move[4].upper()
        except IndexError:
            promotion = None

        return piece, init_pos, new_pos, promotion

    def uci_encoder(self, init_pos, new_pos, promotion=None):
        return "".join((init_pos.pos, new_pos.pos, promotion.lower() if promotion else ""))

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













