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


class Board:
    def __init__(self):
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        # self.board = construct_pawns(self.board)
        # construct_knights(self.board)
        # construct_bishops(self.board)
        construct_rooks(self.board)
        # construct_queens(self.board)
        construct_kings(self.board)

        self.player = "white"  # "white"

        self.kings_pos = ((3, 0), (3, 7))

        self.attacking_pos = {
            "white": {},
            "black": {}
        }

        self.gather_check_spaces(self.kings_pos[1], "white")
        self.gather_check_spaces(self.kings_pos[0], "black")

        print(self.attacking_pos["black"])

    def gather_check_spaces(self, pos, color):
        print("KING_POS: ", pos)
        for row in self.board:
            for piece in row:
                if piece == 0:
                    continue
                elif piece.color == color:
                    piece.piece_attack_check(self, pos)


    def move(self):
        move = input("Input your move (ex. Qa2-a4): ")
        if len(move) == 5:
            move = "".join(("P", move))
        init_pos = cord_to_pos(move[1:3])
        new_pos = cord_to_pos(move[4:6])
        piece = self.board[init_pos[1]][init_pos[0]]
        if piece.sym != move[0]:
            raise UnrecognisableMove(move)
        elif piece.color != self.player:
            raise PieceColorException(piece)

        self.check_for_check(self.kings_pos[0 if self.player == "white" else 1], piece, init_pos, new_pos)

        if (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
            raise ImpossibleMoveException(piece, "Piece can't reach", init_pos, new_pos)

        if self.kings_pos[0 if self.player == "white" else 1] in chain.from_iterable(board.attacking_pos["white" if self.player == "black" else "black"].values()):
            raise ImpossibleMoveException(piece, "need to move king on check", init_pos, new_pos)

        new_pos = piece.move(self, new_pos)

        if self.player == "white":
            self.player = "black"
        else:
            self.player = "white"

        self.update_pos(piece, new_pos)

    def update_pos(self, piece, cord):
        self.board[piece.pos[1]][piece.pos[0]] = 0
        self.board[cord[1]][cord[0]] = piece
        piece.old_pos = piece.pos
        piece.pos = cord
        piece.piece_attack_check(self, self.kings_pos[0 if piece.color == "black" else 1])

    def check_for_check(self, king_pos, piece, init_pos, new_pos):
        print(king_pos)
        king = self.board[king_pos[1]][king_pos[0]]
        king_check = king.check_if_can_go(self, king_pos)
        if king_check:
            return ImpossibleMoveException(piece, "Cant move due to check", init_pos, new_pos)


    def construct(self):
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












