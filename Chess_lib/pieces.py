from Errors import JustError
from position import PositionVector2D

from types import GeneratorType


class Piece:
    # A class for Rook
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        if isinstance(pos, PositionVector2D):
            self.pos = pos
        else:
            self.pos = PositionVector2D(pos)

        self.board = board
        self.name: str
        self.sym: str

        self.color = color if color in ("white", "black") else None

        self.debug = debug

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pass

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pass

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        pass

    def get_line_positions_towards_king(self, king_pos):
        raise JustError

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        pass

    def get_possible_moves(self):
        pass


class Knight(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        super(Knight, self).__init__(board, color, pos, debug=debug)
        self.name = "Knight"
        self.sym = "N" if color == "white" else "n"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = abs(pos - self.pos)
        if pos_change[0] + pos_change[1] == 3 and pos_change[0] != 0 and pos_change[1] != 0:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        piece = self.board.board[pos[1]][pos[0]]
        if piece == 0:
            return False, None
        if piece.color != self.color:
            return False, None
        return True, f"a piece ({piece} is blocking the way on {pos.cord}"

    def get_attacking_squares(self) -> GeneratorType:
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (-2, -1), (2, -1)]
        for i in directions:
            position = self.pos + i
            if 0 <= position[0] <= 7 and 0 <= position[1] <= 7:
                yield position

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        if king_pos in self.get_attacking_squares():
            return True
        return False

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for point in self.get_attacking_squares():
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point


    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield

        for pos in self.get_attacking_squares():
            piece = self.board.board[pos[1]][pos[0]]
            if isinstance(piece, Piece):
                if piece.color != self.color:
                    yield self.board.uci_encoder(self.pos, pos, None)
                continue
            yield self.board.uci_encoder(self.pos, pos, None)


class Rook(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        super(Rook, self).__init__(board, color, pos, debug=debug)
        self.name = "Rook"
        self.sym = "R" if color == "white" else "r"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = abs(pos - self.pos)
        if pos_change[0] == 0 or pos_change[1] == 0:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = pos - self.pos

        points = self.get_line_positions(pos_change)

        for i in list(points):
            piece = self.board.board[i[1]][i[0]]

            if (i == pos and (piece.color != self.color) if isinstance(piece, Piece) else True) or piece == self:
                continue
            elif piece:
                return True, f"a piece ({piece} is blocking the way on {i.cord}"

        return False, None

    def get_line_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        direction = pos_change.normalize()
        for i in range(0, max(abs(pos_change))+1):
            yield self.pos + direction * i

    def attacking_positions_towards_king(self, kings_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        # yields all the points that are towards the king
        pos_change = kings_pos - self.pos
        if abs(pos_change[0]) > abs(pos_change[1]):
            pos_change = PositionVector2D((pos_change[0], 0))
        else:
            pos_change = PositionVector2D((0, pos_change[1]))

        points = self.get_line_positions(pos_change)
        return points

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        if king_pos == list(self.attacking_positions_towards_king(king_pos))[-1]:
            return True
        return False

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for point in self.attacking_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point


    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield

        for i in ((self.pos[0], 0), (self.pos[0], 7), (0, self.pos[1]), (7, self.pos[1])):
            for j in self.get_line_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield self.board.uci_encoder(self.pos, j, None)
                    break
                yield self.board.uci_encoder(self.pos, j, None)


class Bishop(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        super(Bishop, self).__init__(board, color, pos, debug=debug)
        self.name = "Bishop"
        self.sym = "B" if color == "white" else "b"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = abs(pos - self.pos)
        if pos_change[0] == pos_change[1]:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = pos - self.pos

        points = self.get_diagonal_positions(pos_change)

        for i in list(points):
            piece = self.board.board[i[1]][i[0]]

            if (i == pos and (piece.color != self.color) if isinstance(piece, Piece) else True) or piece == self:
                continue
            elif piece:
                return True, f"a piece ({piece} is blocking the way on {i.cord}"

        return False, None

    def get_diagonal_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        direction = pos_change.normalize()
        if direction[0] == 0 or direction[1] == 0:
            direction = PositionVector2D((0, 0))
        for i in range(0, max(abs(pos_change))+1):
            yield self.pos + direction * i

    def attacking_positions_towards_king(self, kings_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        # yields all the points that are towards the king
        pos_change = kings_pos - self.pos
        points = self.get_diagonal_positions(pos_change)
        return points

    # TODO: do we need this method
    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        if king_pos == list(self.attacking_positions_towards_king(king_pos))[-1]:
            return True
        return False

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for point in self.attacking_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point

    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield
        for i in ((7, 0), (0, 7), (0, 0), (7, 7)):
            for j in self.get_diagonal_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield self.board.uci_encoder(self.pos, j, None)
                    break
                yield self.board.uci_encoder(self.pos, j, None)


class Queen(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        super(Queen, self).__init__(board, color, pos, debug=debug)
        self.name = "Queen"
        self.sym = "Q" if color == "white" else "q"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = abs(pos - self.pos)
        if (pos_change[0] == 0 or pos_change[1] == 0) or pos_change[0] == pos_change[1]:
            return True, None

        return False, f"{self.name} can't reach from {self.pos} to {pos}"

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = pos - self.pos

        if pos_change[0] == 0 or pos_change[1] == 0:
            points = self.get_line_positions(pos_change)
        else:
            points = self.get_diagonal_positions(pos_change)


        for i in list(points):
            piece = self.board.board[i[1]][i[0]]

            if (i == pos and (piece.color != self.color) if isinstance(piece, Piece) else True) or piece == self:
                continue
            elif piece:
                return True, f"a piece ({piece} is blocking the way on {i.cord}"

        return False, None

    def get_line_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        direction = pos_change.normalize()
        for i in range(0, max(abs(pos_change))+1):
            yield self.pos + direction * i

    def get_diagonal_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        direction = pos_change.normalize()
        if direction[0] == 0 or direction[1] == 0:
            direction = PositionVector2D((0, 0))
        for i in range(0, max(abs(pos_change))+1):
            yield self.pos + direction * i

    def attacking_positions_towards_king(self, kings_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        # yields all the points that are towards the king
        # in the case of the Queen, will yield 2 lines (vertical/horizontal and diagonal)
        pos_change = kings_pos - self.pos
        yield from self.get_diagonal_positions(pos_change)

        if abs(pos_change[0]) > abs(pos_change[1]):
            pos_change = PositionVector2D((pos_change[0], 0))
        else:
            pos_change = PositionVector2D((0, pos_change[1]))

        yield from self.get_line_positions(pos_change)

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        if king_pos in self.attacking_positions_towards_king(king_pos):
            return True
        return False

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for point in self.attacking_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point


    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield

        for i in ((self.pos[0], 0), (self.pos[0], 7), (0, self.pos[1]), (7, self.pos[1])):
            for j in self.get_line_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield self.board.uci_encoder(self.pos, j, None)
                    break
                yield self.board.uci_encoder(self.pos, j, None)

        for i in ((7, 0), (0, 7), (0, 0), (7, 7)):
            for j in self.get_diagonal_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield self.board.uci_encoder(self.pos, j, None)
                    break
                yield self.board.uci_encoder(self.pos, j, None)


class King(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        super(King, self).__init__(board, color, pos, debug=debug)
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

        attacked, pos_that_attack = self.board.check_if_pos_attacked(pos, self.color)
        return attacked, f"there are pieces in positions {pos_that_attack} that attack the position"

    def get_possible_moves(self) -> GeneratorType:
        yield None  # control yield

        for y_i in range(-1, 2):
            for x_i in range(-1, 2):
                if x_i == y_i == 0:
                    continue
                position = PositionVector2D((self.pos[0] + x_i, self.pos[1] + y_i))
                if not (0 <= position[0] <= 7 and 0 <= position[1] <= 7):
                    continue

                possible_piece = self.board.board[position[1]][position[0]]

                if isinstance(possible_piece, Piece):
                    if possible_piece.color == self.color:
                        continue
                res = self.board.check_if_pos_attacked(position, self.color)
                if not res[0] and (0 <= position[0] <= 7 and 0 <= position[1] <= 7):
                    yield self.board.uci_encoder(self.pos, position, None)

        can_castle = self.board.kings_castle[self.color]

        if not self.board.check:
            if can_castle[0] and self.can_castle(-1)[0]:
                yield self.board.uci_encoder(self.pos, PositionVector2D((2, self.pos[1])), None)
            if can_castle[1] and self.can_castle(1)[0]:
                yield self.board.uci_encoder(self.pos, PositionVector2D((6, self.pos[1])), None)

    def can_castle(self, side: -1 | 1) -> tuple[bool, str | None]:  # king | queen side
        pos_1 = self.pos + PositionVector2D((1, 0)) * side
        pos_2 = self.pos + PositionVector2D((2, 0)) * side
        if isinstance(self.board.board[pos_1[1]][pos_1[0]], Piece) or isinstance(self.board.board[pos_2[1]][pos_2[0]], Piece):
            return False, "piece is blocking the way"
        if self.board.check_if_pos_attacked(pos_1, self.color)[0] is True or self.board.check_if_pos_attacked(pos_2, self.color)[0] is True:
            return False, "the way is attacked"

        return True, None




class Pawn(Piece):
    def __init__(self, board, color: str, pos: tuple[int, int], *, debug=False):
        super(Pawn, self).__init__(board, color, pos, debug=debug)
        self.name = "Pawn"
        self.sym = "P" if color == "white" else "p"

        self.moving_direction = -1 if color == "white" else 1

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> tuple[bool, str | None]:
        pos_change = pos - self.pos
        piece = self.board.board[pos[1]][pos[0]]

        starting_pos_check = self.pos[0] == 6 if self.moving_direction == -1 else self.pos[0] == 1
        # moving normally
        if (pos_change[1] == self.moving_direction or (pos_change[1] == self.moving_direction * 2 and starting_pos_check)) and pos_change[0] == 0:
            if piece == 0:

                return True, None
            return False, f"{piece.name} is blocking the way"

        # capturing a piece
        elif pos_change[1] == self.moving_direction and abs(pos_change[0]) == 1:
            try:
                if piece.color != self.color and isinstance(piece, Piece):
                    return True, None
            except AttributeError:
                pass

            # the en passant logic
            if pos == self.board.possible_en_passant:
                self.board.board[pos[1] - self.moving_direction][pos[0]] = 0
                return True, None

        return False, f"Cant move to the {pos}"

    def blocking_check(self, pos) -> tuple[bool, str | None]:
        return False, None

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        for i in (-1, 1):
            attack_pos = self.pos + (i, self.moving_direction)
            pos_change = king_pos - attack_pos
            if pos_change[0] in (1, 0, -1) and pos_change[1] in (1, 0, -1):
                yield attack_pos

    def is_attacking_king(self, king_pos: PositionVector2D) -> bool:
        pos_change = king_pos - self.pos
        return abs(pos_change[0]) == 1 and pos_change[1] == self.moving_direction

    def get_possible_moves(self) -> GeneratorType:
        yield None # control yield
        # move forward
        if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]] == 0:
            new_pos = PositionVector2D((self.pos[0], self.pos[1]+self.moving_direction))
            # promotion
            if new_pos[1] in (0, 7):
                for letter in ("q", "r", "b", "n"):
                    yield self.board.uci_encoder(self.pos, new_pos, letter)
            else:
                yield self.board.uci_encoder(self.pos, new_pos, None)

        # double move forward
        square_1 = self.board.board[self.pos[1]+2*self.moving_direction][self.pos[0]]
        square_2 = self.board.board[self.pos[1] + self.moving_direction][self.pos[0]]
        starting_pos_check = self.pos[0] == 6 if self.moving_direction == -1 else self.pos[0] == 1

        if square_1 == 0 and square_2 == 0 and starting_pos_check:
            new_pos = PositionVector2D((self.pos[0], self.pos[1] + 2 * self.moving_direction))
            yield self.board.uci_encoder(self.pos, new_pos, None)

        # side capture
        try:
            if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]+1] != 0:
                new_pos = PositionVector2D((self.pos[0]+1, self.pos[1]+self.moving_direction))
                yield self.board.uci_encoder(self.pos, new_pos, None)
        except IndexError:
            pass

        try:
            if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]-1] != 0:
                new_pos = PositionVector2D((self.pos[0]-1, self.pos[1]+self.moving_direction))
                yield self.board.uci_encoder(self.pos, new_pos, None)
        except IndexError:
            pass

        # en_passant
        if self.board.possible_en_passant == (self.pos[0]-1, self.pos[1]+self.moving_direction) or self.board.possible_en_passant == (self.pos[0]+1, self.pos[1]+self.moving_direction):
            yield self.board.uci_encoder(self.pos, self.board.possible_en_passant, None)



