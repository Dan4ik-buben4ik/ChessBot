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

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pass

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pass

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        pass

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        pass

    def get_possible_moves(self):
        pass

    @staticmethod
    def construct(board):
        pass

class Rook(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Rook, self).__init__(board, color, pos)
        self.name = "Rook"
        self.sym = "R" if color == "white" else "r"

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
        points = self.get_line_positions(direction)
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

    def get_line_positions(self, direction: PositionVector2D | tuple[int, int]) -> GeneratorType:
        # make sure it yields only right positions (aka not outside the border)
        if not isinstance(direction, PositionVector2D):
            direction = PositionVector2D(direction)
        pos_boarder_change = abs(direction) * 7

        for i in range(0, max(abs(pos_boarder_change))+1):
            yield self.pos + direction * i

# king_direction_position
    def get_line_positions_towards_king(self, kings_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        # yields all the points that are towards the king
        pos_change = kings_pos - self.pos
        direction = pos_change.normalize()
        # print(direction)
        if abs(pos_change[0]) > abs(pos_change[1]):
            direction = PositionVector2D((direction[0], 0))
        else:
            direction = PositionVector2D((0, direction[1]))

        # print(direction)
        points = self.get_line_positions(direction)
        return points
        # for p in points:
        #     yield p
        #     if p == kings_pos:
        #         break

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        if king_pos in list(self.get_line_positions_towards_king(king_pos)):
            return True
        return False

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for point in self.get_line_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point

# add a decorator that formats the positions into the string
    @PositionVector2D.move_formatting(None)
    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield

        for i in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            for j in self.get_line_positions(i):
                # do this part with try/except? or not needed?
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield j
                    break
                yield j

    @staticmethod
    def construct(board):
        # A function that adds the rooks to the board
        board.board[0][0] = Rook(board, "black", (0, 0))
        board.board[0][7] = Rook(board, "black", (7, 0))
        board.board[7][0] = Rook(board, "white", (0, 7))
        board.board[7][7] = Rook(board, "white", (7, 7))

        # board.board[0][0] = Rook(board, "white", (0, 0))
        # board.board[0][3] = Rook(board, "white", (3, 0))
        # board.board[7][0] = Rook(board, "black", (0, 7))
        # board.board[7][7] = Rook(board, "black", (7, 7))


# class Bishop(Piece):
#     def __init__(self, board, color: str, pos: tuple[int, int]):
#         super(Bishop, self).__init__(board, color, pos)
#         self.name = "Bishop"
#         self.sym = "B" if color == "white" else "b"
#
#     def reach_check(self, pos: tuple[int, int]) -> tuple[bool, str | None]:
#         # Position change. Needed to check if the movement is possible
#         pos_change = abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])
#         if (pos_change[0] != 0 and pos_change[1] != 0) and pos_change[0] == pos_change[1]:
#             return True, None
#
#         return False, f"{self.name} can't reach from {self.pos} to {pos}"
#
#     def blocking_check(self, pos):
#         pos_change = self.pos[0] - pos[0], self.pos[1] - pos[1]
#         direction = pos_change[0] // 1, pos_change[1] // 1
#
#         points = self.get_diagonal_positions(pos_change, direction)
#         for i in points:
#             res = self.board.board[i[0]][i[1]]
#             if res is Piece:
#                 return True
#
#         # Checks if there is a piece on the way
#
#     def get_diagonal_positions(self, pos_change, direction) -> GeneratorType:  # tuple[int, int]
#         for i in range(abs(pos_change[0])):
#             yield self.pos[0] + i * direction[0], self.pos[1] + i * direction[1]
#
#     @staticmethod
#     def construct(board):
#         board.board[0][2] = Bishop(board, "white", (2, 0))
#         board.board[0][5] = Bishop(board, "white", (5, 0))
#         board.board[7][2] = Bishop(board, "black", (2, 7))
#         board.board[7][5] = Bishop(board, "black", (5, 7))

class King(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(King, self).__init__(board, color, pos)
        self.name = "King"
        self.sym = "K" if color == "white" else "k"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        # Position change. Needed to check if the movement is possible
        pos_change = abs(pos - self.pos)
        if pos_change[0] == 1 or pos_change[1] == 1:  # moving
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:  # need to check
        # in case of king, this will check whether the space he wants to go is free.
        piece_in_pos = self.board.board[pos[1]][pos[0]]
        if piece_in_pos != 0:
            if piece_in_pos.color == self.color:
                return True, f"There is a {self.color} piece on the spot"

        attacked, pos_that_attack = self.check_if_pos_attacked(pos)
        return attacked, f"there are pieces in positions {pos_that_attack} that attack the position"

    def move(self, new_pos: PositionVector2D | tuple[int, int]):
        print(f"Moved {self.name} on {self.pos} to {new_pos}")
        self.pos = new_pos

    def check_if_pos_attacked(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, list]:
        # maybe needs to be separated into smaller functions???
        directions_list = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        directions_list = list(map(lambda x: PositionVector2D(x), directions_list))
        direction_del = []
        pos_that_attack = []

        # check for knight
        pos_that_attack.extend(list(self.get_pos_of_knights_attacking_pos(pos)))

        # check for any other pieces
        for i in range(1, 8):
            # print("new_cycle")
            for direction in directions_list:
                # print(f"dir * i = {direction * i}\ntype = {type(direction)}")
                piece_pos = pos + direction * i
                if not (0 <= piece_pos[0] <= 7 and 0 <= piece_pos[1] <= 7):
                    direction_del.append(direction)
                    continue
                # print(piece_pos, piece_pos.cord)
                piece = self.board.board[piece_pos[1]][piece_pos[0]]

                if piece == 0:
                    pass
                elif piece.color == self.color:
                    direction_del.append(direction)

                else:
                    if piece.name in ("Rook", "Queen") and sum(abs(direction)) == 1:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    elif piece.name in ("Bishop", "Queen") and sum(abs(direction)) == 2:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    elif piece.name == "Pawn" and i == 1:  # piece.direction somewhere
                        if (direction[0], direction[1]) in ((-1, -piece.moving_direction), (1, -piece.moving_direction)):
                            pos_that_attack.append(piece_pos)

                    elif piece.name == "King" and i == 1:
                        pos_that_attack.append(piece_pos)
                        # return True, f"{piece.name} is attacking the position"

                    direction_del.append(direction)

            for d in direction_del:
                directions_list.remove(d)
            direction_del = []

        return True if len(pos_that_attack) > 0 else False, pos_that_attack

    def get_pos_of_knights_attacking_pos(self, pos: PositionVector2D) -> GeneratorType:
        knight_directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (-2, -1), (2, -1)]
        piece = 0
        for i in knight_directions:
            knight_pos = pos + i
            try:
                piece = self.board.board[knight_pos[1]][knight_pos[0]]
            except IndexError:
                continue
            finally:
                if piece == 0:
                    continue
                elif piece.name == "Knight" and piece.color != self.color:
                    yield knight_pos

    @PositionVector2D.move_formatting(None)
    def get_possible_moves(self) -> GeneratorType:
        yield None  # control yield

        for y_i in range(-1, 2):
            for x_i in range(-1, 2):
                if x_i == y_i == 0:
                    continue
                position = PositionVector2D((self.pos[0] + x_i, self.pos[1] + y_i))
                res = self.check_if_pos_attacked(position)
                if not res[0] and (0 <= position[0] <= 7 and 0 <= position[1] <= 7):
                    yield position


    def castle(self, new_pos, side: -1 | 1) -> tuple[bool, str | None]:  # king | queen side
        pos_1 = self.check_if_pos_attacked(self.pos + PositionVector2D((1, 0)) * side)
        pos_2 = self.check_if_pos_attacked(self.pos + PositionVector2D((2, 0)) * side)
        if pos_1[0] is True or pos_2[0] is True:
            return False, "the way is attacked"

        return True, None

    @staticmethod
    def construct(board):
        board.board[0][4] = King(board, "black", (4, 0))
        board.board[7][4] = King(board, "white", (4, 7))




class Pawn(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int]):
        super(Pawn, self).__init__(board, color, pos)
        self.name = "Pawn"
        self.sym = "P" if color == "white" else "p"

        self.moving_direction = -1 if color == "white" else 1
        self.can_double = True

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = pos - self.pos
        piece = self.board.board[pos[1]][pos[0]]

        # moving normally
        if (pos_change[1] == self.moving_direction or (pos_change[1] == self.moving_direction * 2 and self.can_double is True)) and pos_change[0] == 0:
            if piece == 0:
                if self.can_double is True:
                    self.can_double = False

                if pos_change[1] == self.moving_direction * 2:
                    self.board.possible_en_passant = self.pos + (0, self.moving_direction)

                return True, None
            return False, f"{piece.name} is blocking the way"

        # capturing a piece
        elif pos_change[1] == self.moving_direction and abs(pos_change[0]) == 1:
            try:
                if piece.color != self.color and isinstance(piece, Piece):
                    return True, None
            except AttributeError:
                pass

            # # the en passant logic
            # en_passant_piece_pos = PositionVector2D((pos[0], pos[1] - self.moving_direction))
            # en_passant_piece_pos_init = PositionVector2D((pos[0], pos[1] + self.moving_direction))
            # en_passant_piece = self.board.board[en_passant_piece_pos[1]][en_passant_piece_pos[0]]

            # the en passant logic
            if pos == self.board.possible_en_passant:
                self.board.board[pos[1] - self.moving_direction][pos[0]] = 0
                return True, None

            # if isinstance(en_passant_piece, Pawn):
            #
            #     if self.board.last_move == (en_passant_piece, en_passant_piece_pos_init, en_passant_piece_pos):  # ***
            #         self.board.board[pos[1] - self.moving_direction][pos[0]] = 0
            #         return True, None
            #     else:
            #         return False, f"can't capture a pawn that hadn't moved 2 squares"
            # return False, f"Cant capture your own piece"

        return False, f"Cant move to the {pos}"

    def blocking_check(self, pos) -> tuple[bool, str | None]:
        return False, None

    # def king_direction_position(self, kings_pos) -> GeneratorType:
    #     for i in (-1, 1):
    #         yield self.pos + (i, self.moving_direction)


    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for i in (-1, 1):
            attack_pos = self.pos + (i, self.moving_direction)
            pos_change = king_pos - attack_pos
            if pos_change[0] in (1, 0, -1) and pos_change[1] in (1, 0, -1):
                print(attack_pos)
                yield attack_pos

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        pos_change = king_pos - self.pos
        return abs(pos_change[0]) == 1 and pos_change[1] == self.moving_direction

    @PositionVector2D.move_formatting(None)
    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield
        # move forward
        if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]] == 0:
            yield PositionVector2D((self.pos[0], self.pos[1]+self.moving_direction))

        if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]+1] != 0:
            yield PositionVector2D((self.pos[0]+1, self.pos[1]+self.moving_direction))

        if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]-1] != 0:
            yield PositionVector2D((self.pos[0]-1, self.pos[1]+self.moving_direction))

        # en_passant
        if self.board.possible_en_passant == (self.pos[0]-1, self.pos[1]+self.moving_direction) or self.board.possible_en_passant == (self.pos[0]+1, self.pos[1]+self.moving_direction):
            yield self.board.possible_en_passant


    @staticmethod
    def construct(board):
        # board.board[4][3] = Pawn(board, "white", (3, 4))
        board.board[3][4] = Pawn(board, "white", (4, 3))

        # board.board[4][3] = Pawn(board, "white", (3, 4))
        # board.board[3][3] = Pawn(board, "white", (3, 3))

