from Errors import JustError
from position import PositionVector2D

from types import GeneratorType


class Piece:
    # A class for Rook
    def __init__(self, board, color: str, pos: tuple[int, int]):
        if isinstance(pos, PositionVector2D):
            self.pos = pos
        else:
            self.pos = PositionVector2D(pos)

        self.board = board
        self.name: str
        self.sym: str

        self.color = color if color in ("white", "black") else None

    def move(self, new_pos):
        print(f"Moved {self.name} on {self.pos} to {new_pos}")
        self.pos = new_pos

    def reach_check(self, pos: tuple[int, int]) -> tuple[bool, str | None]:
        pass

    def blocking_check(self, pos) -> tuple[bool, str | None]:
        pass

    def king_direction_position(self, kings_pos) -> GeneratorType:
        pass

    def around_pos_attack_check(self, pos):  # used to compute if the positions around king are attacked
        pass

    @staticmethod
    def construct(board):
        pass

class Rook(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Rook, self).__init__(board, color, pos)
        self.name = "Rook"
        self.sym = "R"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        # doesn't needed
        # Position change. Needed to check if the movement is possible
        pos_change = abs(pos - self.pos)
        if pos_change[0] != 0 or pos_change[1] != 0:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = pos - self.pos  # == pos - self.pos
        # \/ change using class for pos \/
        direction = pos_change.normalize()
        points = self.get_line_positions(direction, pos_change)
        print(f"blocking check in Rook")
        for i in points:
            piece = self.board.board[i[1]][i[0]]
#            print(i)
#            print(self.board.board[i[1]][i[0]])

            if (i == pos and piece.color != self.color if piece is Piece else True) or piece == self:
                pass
            elif piece:
                return True, f"a piece ({piece} is blocking the way on {i.cord}"

        return False, None

        # Checks if there is a piece on the way

    def get_line_positions(self, direction: PositionVector2D | tuple[int, int], pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:

    #    print(f"direction: {direction} ({type(direction)})\npos_change: {pos_change}")

        for i in range(0, max(abs(pos_change))+1):  # address the issue of last piece not being checked (+1) # address the issue of the rook not taking the piece
            yield self.pos + direction * i

    def king_direction_position(self, kings_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        # print("Rook.king_direction_position()")
        pos_change = kings_pos - self.pos
        direction = pos_change.normalize()
        # print(direction)
        if abs(pos_change[0]) > abs(pos_change[1]):
            direction = PositionVector2D((direction[0], 0))
        else:
            direction = PositionVector2D((0, direction[1]))

        # print(direction)

        pos_boarder_change = abs(direction) * 7
        points = self.get_line_positions(direction, pos_boarder_change)
        for p in points:
            yield p
            if p == kings_pos:
                break



    def around_pos_attack_check(self, king_pos):
        pos_change = king_pos - self.pos
        # \/ change using class for pos \/
        # direction = pos_change[0] // abs(pos_change[0]), 0 if abs(pos_change[0]) > abs(pos_change[1]) else 0, pos_change[1] // abs(pos_change[1])
        direction = pos_change.normalize()
        if direction[0] > direction[1]:
            direction = PositionVector2D((direction[0], 0))
        else:
            direction = PositionVector2D((0, direction[1]))

        pos_boarder_change = abs(direction) * 7  # pos_change from pos to boarder in the needed direction

        points = self.get_line_positions(direction, pos_boarder_change)

        print(f"around_pos_attack_check for {self.name}")
        print(f"points: {list(points)}")
        for p in points:
            delta_p = king_pos - p
            if delta_p[0] in (-1, 0, 1) and delta_p[1] in (-1, 0, 1):
                yield p


    @staticmethod
    def construct(board):
        # A function that adds the rooks to the board
        board.board[0][0] = Rook(board, "white", (0, 0))
        board.board[0][7] = Rook(board, "white", (7, 0))
        board.board[7][0] = Rook(board, "black", (0, 7))
        board.board[7][7] = Rook(board, "black", (7, 7))

class Bishop(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Bishop, self).__init__(board, color, pos)
        self.name = "Bishop"
        self.sym = "B"

    def reach_check(self, pos: tuple[int, int]) -> tuple[bool, str | None]:
        # Position change. Needed to check if the movement is possible
        pos_change = abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])
        if (pos_change[0] != 0 and pos_change[1] != 0) and pos_change[0] == pos_change[1]:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos):
        pos_change = self.pos[0] - pos[0], self.pos[1] - pos[1]
        direction = pos_change[0] // 1, pos_change[1] // 1

        points = self.get_diagonal_positions(pos_change, direction)
        for i in points:
            res = self.board.board[i[0]][i[1]]
            if res is Piece:
                return True

        # Checks if there is a piece on the way

    def get_diagonal_positions(self, pos_change, direction) -> GeneratorType:  # tuple[int, int]
        for i in range(abs(pos_change[0])):
            yield self.pos[0] + i * direction[0], self.pos[1] + i * direction[1]

    @staticmethod
    def construct(board):
        board.board[0][2] = Bishop(board, "white", (2, 0))
        board.board[0][5] = Bishop(board, "white", (5, 0))
        board.board[7][2] = Bishop(board, "black", (2, 7))
        board.board[7][5] = Bishop(board, "black", (5, 7))

class King(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(King, self).__init__(board, color, pos)
        self.name = "King"
        self.sym = "K"
        self.blocked_list = [
            [False, False, False],
            [False, None,  False],
            [False, False, False]
        ]

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        # Position change. Needed to check if the movement is possible
        pos_change = abs(pos - self.pos)
        if pos_change[0] == 1 or pos_change[1] == 1:  # moving
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:  # need to check
        # in case of king, this will check whether the space he wants to go is free.
        piece_in_pos = self.board.board[pos[1]][pos[1]]
        if piece_in_pos != 0:
            if piece_in_pos.color == self.color:
                return True, f"There is a {self.color} piece on the spot"
        attacked, reason = self.check_if_pos_attacked(pos)
        return attacked, reason

    def move(self, new_pos: PositionVector2D | tuple[int, int]):
        print(f"Moved {self.name} on {self.pos} to {new_pos}")
        self.pos = new_pos


    def check_if_pos_attacked(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        directions_list = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        directions_list = list(map(lambda x: PositionVector2D(x), directions_list))
        direction_del = []
        print("King.check_if_pos_attacked")

        # check for knight
        knight_pos = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (-2, -1), (2, -1)]
        for i in knight_pos:
            piece = self.board.board[i[1]][i[0]]
            if piece == 0:
                continue
            elif piece.name == "Knight" and piece.color != self.color:
                return True, f"knight is attacking the pos"

        for i in range(1, 8):
            print("new_cycle")
            for direction in directions_list:
                # print(f"dir * i = {direction * i}\ntype = {type(direction)}")
                piece_pos = pos + direction * i
                if not (0 <= piece_pos[0] <= 7 and 0 <= piece_pos[1] <= 7):
                    direction_del.append(direction)
                    continue
                print(piece_pos, piece_pos.cord)
                piece = self.board.board[piece_pos[1]][piece_pos[0]]

                if piece == 0:
                    pass
                elif piece.color == self.color:
                    direction_del.append(direction)
                else:
                    if piece.name in ("Rook", "Queen") and sum(abs(direction)) == 1:
                        return True, f"{piece.name} is attacking the position"
                    elif piece.name in ("Bishop", "Queen") and sum(abs(direction)) == 2:
                        return True, None
                    elif piece.name == "Pawn" and i == 1 and (direction[0], direction[1]) in ((-1, -1), (-1, 1)):
                        return True, None
                    else:
                        direction_del.append(direction)

            for d in direction_del:
                directions_list.remove(d)
            direction_del = []

        return False, None


    def update_blocked_list(self, new_pos: PositionVector2D | tuple[int, int]):
        self.blocked_list = [
            [False, False, False],
            [False, None,  False],
            [False, False, False]
        ]

        for y, row in enumerate(self.board.board):
            for x, piece in enumerate(row):
                pos_change = new_pos - (x, y) if type(new_pos) is PositionVector2D else PositionVector2D((new_pos[0] - x, new_pos[1] - y))
                if piece is self or piece == 0:
                    pass
                elif piece.color == self.color and (pos_change[0] in (-1, 0, 1) and pos_change[0] in (-1, 0, 1)):
                    self.blocked_list[pos_change[1]+1][pos_change[0]+1] = True
                else:  # implement a function for the pieces to find the closest path to king and check if it is near
                    for i in piece.around_pos_attack_check(self.pos):
                        print(f"King.update_blocked_list()\ni: {i}")
                        self.blocked_list[i[1]][i[0]] = True


    def castle(self, new_pos, side: -1 | 1) -> tuple[bool, str | None]:  # king | queen side
        print(f"in King.castle()\n pos_1: {self.pos + PositionVector2D((1, 0)) * side}\n pos_2 : {self.pos + PositionVector2D((2, 0)) * side}")
        pos_1 = self.check_if_pos_attacked(self.pos + PositionVector2D((1, 0)) * side)
        pos_2 = self.check_if_pos_attacked(self.pos + PositionVector2D((2, 0)) * side)
        if pos_1[0] is True or pos_2[0] is True:
            return False, "the way is attacked"

        return True, None


    @staticmethod
    def construct(board):
        board.board[0][3] = King(board, "white", (3, 0))
        board.board[7][3] = King(board, "black", (3, 7))



