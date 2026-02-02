
# from Pieces.Bishop import *
# from Pieces.Rook import *
# from Pieces.King import *
from pieces import Piece, Rook, King, Bishop

from util import cord_to_pos
from Errors import UnrecognisableMove, PieceColorException, ImpossibleMoveException

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


# Board Visualisation (with coordinate system on the axis and positions in the squares)
#                       White
#         0     1     2     3     4     5     6     7
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  0   | A1  | B1  | C1  | D1  | E1  | F1  | G1  | H1  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  1   | A2  | B2  | C2  | D2  | E2  | F2  | G2  | H2  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  2   | A3  | B3  | C3  | D3  | E3  | F3  | G3  | H3  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  3   | A4  | B4  | C4  | D4  | E4  | F4  | G4  | H4  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  4   | A5  | B5  | C5  | D5  | E5  | F5  | G5  | H5  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  5   | A6  | B6  | C6  | D6  | E6  | F6  | G6  | H6  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  6   | A7  | B7  | C7  | D7  | E7  | F7  | G7  | H7  |
#      |-----|-----|-----|-----|-----|-----|-----|-----|
#  7   | A8  | B8  | C8  | D8  | E8  | F8  | G8  | H8  |
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
        self.kings_pos = ((3, 0), (3, 7))

        # later use
        self.kings_surroundings = {}
        self.check_line = []

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
        init_pos = cord_to_pos(move[1:3])  # gets the first (old) position eg. Qa2-a4 -> a2
        new_pos = cord_to_pos(move[4:6])  # gets the second (new) position eg. Qa2-a4 -> a4
        return move, init_pos, new_pos


    @staticmethod
    def is_reachable_move(piece, init_pos, new_pos):

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

        # check if it is on the board
        self.is_reachable_move(piece, init_pos, new_pos)

        # in development
        is_check = self.in_check(self.kings_pos[0 if self.player == "white" else 1], piece, init_pos, new_pos)

        # piece class checks
        reach, reason = piece.reach_check(new_pos, en_passan=False) # needed ???
        if not reach:
            raise ImpossibleMoveException(piece, reason, init_pos, new_pos)
        piece.blocking_check(new_pos)
        # After all of the basic checks, calls the piece to check if it can move, and then moves it

        # changes the current player, aka the turn
        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"

        # updates the position of the piece. Might need to be recoded
        self.update_pos(piece, new_pos)

    def update_pos(self, piece: Piece, cord: tuple[int, int]) -> None:  # !!!
        print(f"UPDATE position: {piece}")
        # A function that updates the pieces position on the board
        self.board[piece.pos[1]][piece.pos[0]] = 0  # makes the old square empty
        print(self.board[piece.pos[1]][piece.pos[0]])
        self.board[cord[1]][cord[0]] = piece  # puts the pieces symbol on the new spot
        piece.move(cord)

    def in_check(self, king_pos, piece, init_pos, new_pos) -> bool:  # !!!!!! Change
        # A function that checks if the king is under the attack, via the brute force
        print("In development. Assume returns False")
        return False


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
        for letter in range(104, 96, -1):
            print(f"{chr(letter)}     ", end="")
        print(f"\n{'           ' * 2}Black")













