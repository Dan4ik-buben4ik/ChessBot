
# from Pieces.Bishop import *
# from Pieces.Rook import *
# from Pieces.King import *
from pieces import Piece, Rook, King, Bishop

from Errors import UnrecognisableMove, PieceColorException, ImpossibleMoveException, UnderCheckException, JustError
from position import PositionVector2D

from itertools import chain

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
#                       White
#         0     1     2     3     4     5     6     7
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  0   | H1  | G1  | F1  | E1  | D1  | C1  | B1  | A1  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  1   | H2  | G2  | F2  | E2  | D2  | C2  | B2  | A2  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  2   | H3  | G3  | F3  | E3  | D3  | C3  | B3  | A3  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  3   | H4  | G4  | F4  | E4  | D4  | C4  | B4  | A4  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  4   | H5  | G5  | F5  | E5  | D5  | C5  | B5  | A5  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  5   | H6  | G6  | F6  | E6  | D6  | C6  | B6  | A6  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  6   | H7  | G7  | F7  | E7  | D7  | C7  | B7  | A7  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  7   | H8  | G8  | F8  | E8  | D8  | C8  | B8  | A8  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|

class Board:
    def __init__(self):
        # Create a 2d array with empty (0) squares
        self.board = [[0 for _ in range(8)] for _ in range(8)]

        # Functions that are called for the board to add pieces starting position.
        # self.board = construct_pawns(self.board)
        # construct_knights(self.board)
        # Bishop.construct(self)
        Rook.construct(self)
        # construct_queens(self.board)
        King.construct(self)


        # establishes whose move it is currently
        self.player = "white"  # "white"

        # stores king's position (useful for checks)

        # check
        self.check = False
        self.attack_line = []

        # collapse in 1 dict?
        self.kings_pos = {"white": PositionVector2D((3, 0)), "black": PositionVector2D((3, 7))}
        self.kings_castle = {"white": [True, True], "black": [True, True]}  # king, queen side

    @staticmethod
    def input_move():
        # Getting the move in a format of: Piece Position - New Position
        move = input("Input your move (ex. Qa2-a4): ")

        # checks if there are only positions given , then add P for pawn
        # (e2-e4 is a valid move with pawn, put it doesn't have a piece symbol in front, so we add P)
        if len(move) == 5:
            move = "".join(("P", move))

        # Here is going to be a check for the format of the input, but it is later

        # Getting new and old position
        init_pos = PositionVector2D.cord_to_pos(move[1:3])  # gets the first (old) position eg. Qa2-a4 -> a2
        new_pos = PositionVector2D.cord_to_pos(move[4:6])  # gets the second (new) position eg. Qa2-a4 -> a4
        return move, init_pos, new_pos


    @staticmethod
    def is_reachable_move(piece, init_pos, new_pos) -> None:

        # checks if the move is within the board
        if (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
            raise ImpossibleMoveException(piece, "Piece can't reach", init_pos, new_pos)

        # Checks if the piece is actually moving
        if init_pos == new_pos:
            raise ImpossibleMoveException(piece, "Piece doesn't move", init_pos, new_pos)


    def move(self) -> None:
        # getting the piece
        move_txt, init_pos, new_pos = self.input_move()
        piece: Piece | 0 = self.board[init_pos[1]][init_pos[0]]

        # checks the symbol and colour of the piece
        if piece == 0:  # if the square is empty, raises error
            raise UnrecognisableMove(move_txt)
        elif piece.color != self.player:  # if the pieces colour is not of the current players turn, raises error
            raise PieceColorException(piece)

        # identifier that helps to see methods
        piece: Piece

        # check if currently under check
        print(f" the king is under check: {self.check}")
        if self.check:
            # surely final pos or the king movement
            if new_pos not in self.attack_line and not isinstance(piece, King):
                raise ImpossibleMoveException(piece, f"attacking on {self.kings_pos[self.player]} is under check", init_pos, new_pos)


        # check for checks
        # if self.check:
        #     if not isinstance(piece, King):
        #         raise UnderCheckException(move_txt, self.kings_pos[self.player])

        # checks if castle or en_passan
        pos_change = new_pos - init_pos
        if isinstance(piece, King) and self.kings_castle[self.player] == [True, True]:
            print("checked king in board.move()")
            if abs(pos_change[0]) == 2 and pos_change[1] == 0:
                if self.check is True:
                    raise ImpossibleMoveException(piece, f"attacking on {self.kings_pos[self.player]} is under check", init_pos, new_pos)

                print("king is castling...")
                self.castle(piece, init_pos, new_pos, pos_change)
                return
            else:
                self.kings_castle[self.player][PositionVector2D.sign(pos_change[0])] = False

        # check if it is on the board
        self.is_reachable_move(piece, init_pos, new_pos)


        # piece class checks
        reach, reason = piece.reach_check(new_pos)
        if not reach:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)
        blocking, reason = piece.blocking_check(new_pos)
        if blocking:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)
        # After all of the basic checks, calls the piece to check if it can move, and then moves it

        # in development


        # updates the position of the piece. Might need to be recoded
        self.update_pos(piece, new_pos)

        opponent_king_pos = self.kings_pos["black" if self.player == "white" else "white"]
        opponent_king: King = self.board[opponent_king_pos[1]][opponent_king_pos[0]]
        is_check, attack_points = self.king_check(opponent_king.pos, piece, init_pos, new_pos)
        if is_check:
            self.check = True
            print("check on the king")
            self.attack_line = attack_points
            opponent_king.update_blocked_list(opponent_king.pos)

        # changes the current player, aka the turn
        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"

    def update_pos(self, piece: Piece, cord: tuple[int, int]) -> None:  # !!!
        print(f"UPDATE position: {piece}")
        # A function that updates the pieces position on the board
        self.board[piece.pos[1]][piece.pos[0]] = 0  # makes the old square empty
        print(self.board[piece.pos[1]][piece.pos[0]])
        self.board[cord[1]][cord[0]] = piece  # puts the pieces symbol on the new spot
        piece.move(cord)

        if isinstance(piece, King):
            self.kings_pos[piece.color] = cord

    def king_check(self, king_pos: PositionVector2D, piece: Piece, init_pos, new_pos) -> tuple[bool, list | None]:  # !!!!!! Change
        # A function that checks if the king is under the attack, via the brute force
        if isinstance(piece, King):
            return False, None
        attack_points = list(piece.king_direction_position(king_pos))
        print("Board.king_check()")
        print(f"attack pos {attack_points}")
        print(king_pos)
        if king_pos in attack_points:
            return True, attack_points
        return False, None

    def castle(self, piece, init_pos, new_pos, pos_change) -> None:
        direction = PositionVector2D.sign(pos_change[0])
        if self.kings_castle[self.player][direction] is False:
            raise ImpossibleMoveException(piece, "The king/rook had already moved", init_pos, new_pos)

        king: King = piece
        can_castle, reason = king.castle(new_pos, direction)
        if can_castle is False:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)

        rook_pos = 0 if direction == -1 else 7, new_pos[1]
        print(f"rook pos in board.castle(): {rook_pos}")
        rook: Rook = self.board[rook_pos[1]][rook_pos[0]]

        rook_new_pos = rook_pos[0] - 3 if direction == 1 else rook_pos[0] + 2, rook_pos[1]

        # changes the current player, aka the turn
        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"

        self.update_pos(king, new_pos)
        self.update_pos(rook, rook_new_pos)





    def construct(self):
        # A function that prints the board. NOTHING TO BE CHANGED HERE
        print(f"{'           ' * 2}White")
        num = 1  # h - 104, a - 97
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
            num += 1
            print("|-----" * 8 + "|")

        # section to add letters
        print("   ", end="")
        # h - 104, a - 97
        for letter in range(104, 96, -1):  # H -> A
            print(f"{chr(letter)}     ", end="")
        print(f"\n{'           ' * 2}Black")













