from Pieces import *
from util import pos_to_cord, cord_to_pos
from Errors import UnrecognisableMove, PieceColorException, ImpossibleMoveException

from itertools import chain

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
        construct_knights(self.board)
        # construct_bishops(self.board)
        construct_rooks(self.board)
        # construct_queens(self.board)
        construct_kings(self.board)

        # establishes whose move it is currently
        self.player = "white"  # "white"

        # stores king's position (useful for checks)
        self.kings_pos = ((3, 0), (3, 7))

        # A dict that stores the squares that are under attack (WILL BE CHANGED)
        self.attacking_pos = {
            "white": {},
            "black": {}
        }

        # Function that gathers the checks from all of the pieces
        self.gather_check_spaces(self.kings_pos[1], "white")
        self.gather_check_spaces(self.kings_pos[0], "black")

        # print(self.attacking_pos["black"])

    def gather_check_spaces(self, pos, color) -> None:
        #  A function tha gathers all of the attacked squares
        #  by brute forcing through whole board and all of the pieces (WILL BE DELETED)
        print("KING_POS: ", pos)

        # checks through each row
        for row in self.board:
            # checks each piece
            for piece in row:
                # if empty, we skip
                if piece == 0:
                    continue
                elif piece.color == color:
                    piece.piece_attack_check(self, pos)


    def move(self) -> None:
        # a function to move a piece on the board

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

        # getting the piece
        piece = self.board[init_pos[1]][init_pos[0]]

        # checks the symbol and colour of the piece
        if piece.sym != move[0]:  # if the square is empty, raises error
            raise UnrecognisableMove(move)
        elif piece.color != self.player:  # if the pieces colour is not of the current players turn, raises error
            raise PieceColorException(piece)


        # gathers all squares that are under attack. WILL BE DELETED
        self.check_for_check(self.kings_pos[0 if self.player == "white" else 1], piece, init_pos, new_pos)

        # checks if the move is within the board
        if (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
            raise ImpossibleMoveException(piece, "Piece can't reach", init_pos, new_pos)

        # check if king is under attack. WILL BE DELETED AND RE_MADE
        if self.kings_pos[0 if self.player == "white" else 1] in chain.from_iterable(self.attacking_pos["white" if self.player == "black" else "black"].values()):
            raise ImpossibleMoveException(piece, "need to move king on check", init_pos, new_pos)

        # After all of the basic checks, calls the piece to check if it can move, and then moves it
        new_pos = piece.move(self, new_pos)

        # changes the current player, aka the turn
        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"

        # updates the position of the piece. Might need to be recoded
        self.update_pos(piece, new_pos)

    def update_pos(self, piece, cord):
        # A function that updates the pieces position on the board
        self.board[piece.pos[1]][piece.pos[0]] = 0  # makes the old square empty
        self.board[cord[1]][cord[0]] = piece  # puts the pieces symbol on the new spot
        piece.old_pos = piece.pos  # updates the old coordinates within the piece
        piece.pos = cord  # updates the coordinates within the piece

        # adds new squares that are under attack. WILL BE DELETED
        piece.piece_attack_check(self, self.kings_pos[0 if piece.color == "black" else 1])

    def check_for_check(self, king_pos, piece, init_pos, new_pos):
        # A function that checks if the king is under the attack, via the brute force
        print(king_pos)
        king = self.board[king_pos[1]][king_pos[0]]
        king_check = king.check_if_can_go(self, king_pos)
        if king_check:
            return ImpossibleMoveException(piece, "Cant move due to check", init_pos, new_pos)


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













