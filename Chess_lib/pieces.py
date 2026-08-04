from position import PositionVector2D
from util import TurnColor
from Move import Move

from types import GeneratorType


class Piece:
    """ A base class for chess pieces

    It holds all the basic methods
    All the pieces must inherit this class and override the methods

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :ivar color: the piece's color
    :type color: utils.TurnColor

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        if isinstance(pos, PositionVector2D):
            self.pos = pos
        else:
            self.pos = PositionVector2D(pos)

        self.board = board
        self.name: str = ""
        self.sym: str = ""

        self.color = color

        self.debug = debug

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the piece and it's move logic

        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pass

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the path to the position is blocked by another piece

        :param pos: target position
        :type pos: position.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pass

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        """ finds and yields all the reachable squares around the king position

        *Note: this is an optional method. Every class overrides it except Pawn*

        :param king_pos: the position of the king
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        pass

    def attacking_positions_towards_king(self, king_pos):
        """ a method to ge the attacking line towards the king, stopping at the king

        *Note: this is an optional method and is only modified in classes (Bishop, Rook, Queen)*

        :param king_pos: the king position
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        pass

    def get_possible_moves(self):
        """ generates every possible move for the piece in the current position in the board

        *Note: when overriden, the first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *


        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[Move.Move]
        """
        pass


class Knight(Piece):
    """ A class for the Knight piece

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        super(Knight, self).__init__(board, color, pos, debug=debug)
        self.name = "Knight"
        self.sym = "N" if color == TurnColor.WHITE else "n"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the Knight


        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = abs(pos - self.pos)
        if pos_change[0] + pos_change[1] == 3 and pos_change[0] != 0 and pos_change[1] != 0:
            return True

        return False

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the path to the position is blocked by another piece

        :param pos: target position
        :type pos: position.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        piece = self.board.board[pos[1]][pos[0]]
        if piece == 0:
            return False
        if piece.color != self.color:
            return False
        return True

    def _get_attacking_squares(self) -> GeneratorType:
        """ a helper function to get the sauares attacked/deffended by the Knight

        :return:
        """
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (-2, -1), (2, -1)]
        for i in directions:
            position = self.pos + i
            if 0 <= position[0] <= 7 and 0 <= position[1] <= 7:
                yield position

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        """ finds and yields all the reachable squares around the king position

        :param king_pos: the position of the king
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        for point in self._get_attacking_squares():
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point

    def get_possible_moves(self) -> GeneratorType:
        """ generates every possible move for the piece in the current position in the board

        *Note: The first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *

        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[Move.Move]
        """
        yield None # control yield

        for pos in self._get_attacking_squares():
            piece = self.board.board[pos[1]][pos[0]]
            if isinstance(piece, Piece):
                if piece.color != self.color:
                    yield Move(self.pos, pos, None)
                continue
            yield Move(self.pos, pos, None)


class Rook(Piece):
    """ A class for the Knight piece

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        super(Rook, self).__init__(board, color, pos, debug=debug)
        self.name = "Rook"
        self.sym = "R" if color == TurnColor.WHITE else "r"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the piece and it's move logic

        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = abs(pos - self.pos)
        if pos_change[0] == 0 or pos_change[1] == 0:
            return True

        return False

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the path to the position is blocked by another piece

        This function just iterates through all the positions from hte current to the final position
        and checks if any are blocked

        :param pos: target position
        :type pos: position.PositionVector2D

        :return: True/False
        :rtype: bool
        """

        for i in self._get_line_positions(pos - self.pos):
            piece = self.board.board[i[1]][i[0]]

            if (i == pos and (piece.color != self.color) if isinstance(piece, Piece) else True) or piece == self:
                continue
            elif piece:
                return True

        return False

    def _get_line_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ private method that generates positions based on the pieces current position, and the change vector

        :param pos_change: the difference between the target and current position
        :type pos_change: position.PositionVector2D

        :return: a generator object with the position squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        direction = pos_change.normalize()
        for i in range(0, max(abs(pos_change).position)+1):
            yield self.pos + direction * i

    def attacking_positions_towards_king(self, king_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ a method to ge the attacking line towards the king, stopping at the king

        This function finds the difference between self and the king, and gets the positions
        from a line passing closest to the king, obeying the Rook's movement rules

        :param king_pos: the king position
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """

        # yields all the points that are towards the king
        pos_change = king_pos - self.pos
        if abs(pos_change[0]) > abs(pos_change[1]):
            pos_change = PositionVector2D((pos_change[0], 0))
        else:
            pos_change = PositionVector2D((0, pos_change[1]))

        yield from self._get_line_positions(pos_change)

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        """ finds and yields all the reachable squares around the king position

        :param king_pos: the position of the king
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        for point in self.attacking_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point

    def get_possible_moves(self) -> GeneratorType:
        """ generates every possible move for the piece in the current position in the board

        *Note: The first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *

        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[Move.Move]
        """
        yield None # control yield

        for i in ((self.pos[0], 0), (self.pos[0], 7), (0, self.pos[1]), (7, self.pos[1])):
            for j in self._get_line_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield Move(self.pos, j, None)
                    break
                yield Move(self.pos, j, None)


class Bishop(Piece):
    """ A class for the Knight piece

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        super(Bishop, self).__init__(board, color, pos, debug=debug)
        self.name = "Bishop"
        self.sym = "B" if color == TurnColor.WHITE else "b"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the piece and it's move logic

        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = abs(pos - self.pos)
        if pos_change[0] == pos_change[1]:
            return True

        return False

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the path to the position is blocked by another piece

        :param pos: target position
        :type pos: position.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = pos - self.pos

        points = self._get_diagonal_positions(pos_change)

        for i in list(points):
            piece = self.board.board[i[1]][i[0]]

            if (i == pos and (piece.color != self.color) if isinstance(piece, Piece) else True) or piece == self:
                continue
            elif piece:
                return True

        return False

    def _get_diagonal_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ a private method to get the diagonal position towards a certain point

        *Note: the point can be out of the reach, but the function will still yield a diagonal
         that passes closes to the point *

        :param pos_change: the difference between current position and the target point
        :type pos_change: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        direction = pos_change.normalize()
        if direction[0] == 0 or direction[1] == 0:
            direction = PositionVector2D((0, 0))
        for i in range(0, max(abs(pos_change).position)+1):
            yield self.pos + direction * i

    def attacking_positions_towards_king(self, king_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ a method to ge the attacking line towards the king, stopping at the king

        This method finds the position difference between the piece and the king and gets the diagonal points

        :param king_pos: the king position
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        # yields all the points that are towards the king
        yield from self._get_diagonal_positions(king_pos - self.pos)

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        """ finds and yields all the reachable squares around the king position

        :param king_pos: the position of the king
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        for point in self.attacking_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point

    def get_possible_moves(self) -> GeneratorType:
        """ generates every possible move for the piece in the current position in the board

        *Note: The first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *

        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[Move.Move]
        """
        yield None # control yield
        for i in ((7, 0), (0, 7), (0, 0), (7, 7)):
            for j in self._get_diagonal_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield Move(self.pos, j, None)
                    break
                yield Move(self.pos, j, None)


class Queen(Piece):
    """ A class for the Knight piece

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        super(Queen, self).__init__(board, color, pos, debug=debug)
        self.name = "Queen"
        self.sym = "Q" if color == TurnColor.WHITE else "q"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the piece and it's move logic

        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = abs(pos - self.pos)
        if (pos_change[0] == 0 or pos_change[1] == 0) or pos_change[0] == pos_change[1]:
            return True

        return False

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the path to the position is blocked by another piece

        :param pos: target position
        :type pos: position.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = pos - self.pos

        if pos_change[0] == 0 or pos_change[1] == 0:
            points = self._get_line_positions(pos_change)
        else:
            points = self._get_diagonal_positions(pos_change)

        for i in list(points):
            piece = self.board.board[i[1]][i[0]]

            if (i == pos and (piece.color != self.color) if isinstance(piece, Piece) else True) or piece == self:
                continue
            elif piece:
                return True

        return False

    def _get_line_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ a private method used to get the closest vertical/horizontal line positions towards the target

        *Note: despite the similarity with the _get_diagonal_positions() function, here, the pos_change should
         have either the x/y equal to 0 *

        :param pos_change: the difference vector between the target point and the current position
        :type pos_change: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        direction = pos_change.normalize()
        for i in range(0, max(abs(pos_change).position)+1):
            yield self.pos + direction * i

    def _get_diagonal_positions(self, pos_change: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ a private method used to get the closest vertical/horizontal line positions towards the target

        *Note: the point can be out of the reach, but the function will still yield a diagonal
         that passes closes to the point *

        :param pos_change: the difference vector between the target point and the current position
        :type pos_change: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        direction = pos_change.normalize()
        if direction[0] == 0 or direction[1] == 0:
            direction = PositionVector2D((0, 0))
        for i in range(0, max(abs(pos_change).position)+1):
            yield self.pos + direction * i

    def attacking_positions_towards_king(self, king_pos: PositionVector2D | tuple[int, int]) -> GeneratorType:
        """ a method to ge the attacking line towards the king, stopping at the king

        *Note: this is an optional method and is only modified in classes (Bishop, Rook, Queen)*

        :param king_pos: the king position
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        pos_change = king_pos - self.pos
        yield from self._get_diagonal_positions(pos_change)

        if abs(pos_change[0]) > abs(pos_change[1]):
            pos_change = PositionVector2D((pos_change[0], 0))
        else:
            pos_change = PositionVector2D((0, pos_change[1]))

        yield from self._get_line_positions(pos_change)

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        """ finds and yields all the reachable squares around the king position

        :param king_pos: the position of the king
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        for point in self.attacking_positions_towards_king(king_pos):
            pos_change = king_pos - point
            if pos_change[0] in (-1, 0, 1) and pos_change[1] in (-1, 0, 1):
                yield point

    def get_possible_moves(self) -> GeneratorType:
        """ generates every possible move for the piece in the current position in the board

        *Note: The first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *

        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[Move.Move]
        """
        yield None # control yield

        for i in ((self.pos[0], 0), (self.pos[0], 7), (0, self.pos[1]), (7, self.pos[1])):
            for j in self._get_line_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield Move(self.pos, j, None)
                    break
                yield Move(self.pos, j, None)

        for i in ((7, 0), (0, 7), (0, 0), (7, 7)):
            for j in self._get_diagonal_positions(self.pos * -1 + i):
                if not (0 <= j[0] <= 7 and 0 <= j[1] <= 7):
                    break
                elif j == self.pos:
                    continue
                piece = self.board.board[j[1]][j[0]]
                if isinstance(piece, Piece):
                    if piece.color != self.color:
                        yield Move(self.pos, j, None)
                    break
                yield Move(self.pos, j, None)


class King(Piece):
    """ A class for the Knight piece

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        super(King, self).__init__(board, color, pos, debug=debug)
        self.name = "King"
        self.sym = "K" if color == TurnColor.WHITE else "k"

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the piece and it's move logic

        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        # Position change. Needed to check if the movement is possible
        pos_change = abs(pos - self.pos)
        if pos_change[0] == 1 or pos_change[1] == 1:  # moving
            return True

        return False

    def blocking_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the path to the position is blocked by another piece

        :param pos: target position
        :type pos: position.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        # in case of king, this will check whether the space he wants to go is free.
        piece_in_pos = self.board.board[pos[1]][pos[0]]
        if piece_in_pos != 0:
            if piece_in_pos.color == self.color:
                return True

        attacked, pos_that_attack = self.board.check_if_pos_attacked(pos, self.color)
        return attacked

    def get_possible_moves(self) -> GeneratorType:
        """ generates every possible move for the piece in the current position in the board

        *Note: The first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *

        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[MOve.Move]
        """
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
                    yield Move(self.pos, position, None)

        can_castle = self.board.castling_rights[self.color]

        if not self.board.check_if_king_attacked(self.color):
            if can_castle[0] and self._can_castle(-1):
                yield Move(self.pos, PositionVector2D((2, self.pos[1])), None)
            if can_castle[1] and self._can_castle(1):
                yield Move(self.pos, PositionVector2D((6, self.pos[1])), None)

    def _can_castle(self, side: -1 | 1) -> bool:  # king | queen side
        """ a private method that determines whether the king can castle to a particular side

        *Note: the side is the x sign value of the difference between the position after castling
         and the kings current position *

        :param side: the side the king castles
        :type side: int

        :return: if there are any pieces blocking the way or attacking the way
        :rtype: bool
        """
        pos_1 = self.pos + PositionVector2D((1, 0)) * side
        pos_2 = self.pos + PositionVector2D((2, 0)) * side
        if isinstance(self.board.board[pos_1[1]][pos_1[0]], Piece) or isinstance(self.board.board[pos_2[1]][pos_2[0]], Piece):
            return False
        if self.board.check_if_pos_attacked(pos_1, self.color)[0] is True or self.board.check_if_pos_attacked(pos_2, self.color)[0] is True:
            return False

        return True




class Pawn(Piece):
    """ A class for the Knight piece

    :ivar pos: the piece position on the board
    :type pos: position.PositionVector2D

    :ivar board: the board instance where the piece is at
    :type board: loader.Board

    :ivar debug: enables cmd state outputs
    :type debug: bool

    :var name: the name of the piece (allways titled)
    :type name: str

    :var sym: symbol of the piece (upper if white, lower if black)
    :type sym: str
    """
    def __init__(self, board, color: TurnColor, pos: tuple[int, int], *, debug=False):
        """ Initializes the basic class instance variables """
        super(Pawn, self).__init__(board, color, pos, debug=debug)
        self.name = "Pawn"
        self.sym = "P" if color == TurnColor.WHITE else "p"

        self.moving_direction = -1 if color == TurnColor.WHITE else 1

    def reach_check(self, pos: PositionVector2D | tuple[int, int]) -> bool:
        """ Checks if the position is reachable by the piece and it's move logic

        *Note: the function is split in 3 sections, checking capture, en passant and normal movement separately

        :param pos: target position
        :type pos: posiiton.PositionVector2D

        :return: True/False
        :rtype: bool
        """
        pos_change = pos - self.pos
        piece = self.board.board[pos[1]][pos[0]]

        starting_pos_check = self.pos[0] == 6 if self.moving_direction == -1 else self.pos[0] == 1
        # moving normally
        if (pos_change[1] == self.moving_direction or (pos_change[1] == self.moving_direction * 2 and starting_pos_check)) and pos_change[0] == 0:
            if piece == 0:

                return True
            return False

        # capturing a piece
        elif pos_change[1] == self.moving_direction and abs(pos_change[0]) == 1:
            try:
                if piece.color != self.color and isinstance(piece, Piece):
                    return True
            except AttributeError:
                pass

            # the en passant logic

        return False

    def blocking_check(self, pos) -> bool:
        """ Checks if the path to the position is blocked by another piece


        :param pos: target position
        :type pos: position.PositionVector2D

        :return: False
        :rtype: bool
        """
        piece = self.board.board[pos[1]][pos[0]]
        if isinstance(piece, Piece):
            return True
        return False

    def get_positions_attacking_around_king(self, king_pos) -> GeneratorType:
        """ finds and yields all the reachable squares around the king position

        :param king_pos: the position of the king
        :type king_pos: position.PositionVector2D

        :return: generator object with the squares
        :rtype: collections.abc.Generator[position.PositionVector2D]
        """
        for i in (-1, 1):
            attack_pos = self.pos + (i, self.moving_direction)
            pos_change = king_pos - attack_pos
            if pos_change[0] in (1, 0, -1) and pos_change[1] in (1, 0, -1):
                yield attack_pos

    def get_possible_moves(self) -> GeneratorType:
        """ generates every possible move for the piece in the current position in the board

        *Note: The first element yielded is always None, as to prevent empty generator issues
        and to ensure that the collection of the elements are smooth.

        Basically, allways write next(generated_obj) before handling it *

        :return: a generator object with uci encoded moves
        :rtype: collections.abc.Generator[Move.Move]
        """
        yield None # control yield
        # move forward
        if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]] == 0:
            new_pos = PositionVector2D((self.pos[0], self.pos[1]+self.moving_direction))
            # promotion
            if new_pos[1] in (0, 7):
                for letter in ("q", "r", "b", "n"):
                    yield Move(self.pos, new_pos, letter)
            else:
                yield Move(self.pos, new_pos, None)

        # double move forward
        square_1 = self.board.board[self.pos[1]+2*self.moving_direction][self.pos[0]]
        square_2 = self.board.board[self.pos[1] + self.moving_direction][self.pos[0]]
        starting_pos_check = (self.pos[1] == 6 if self.color == TurnColor.WHITE else self.pos[1] == 1)

        if square_1 == 0 and square_2 == 0 and starting_pos_check:
            new_pos = PositionVector2D((self.pos[0], self.pos[1] + 2 * self.moving_direction))
            yield Move(self.pos, new_pos, None)

        # side capture
        try:
            if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]+1] != 0:
                new_pos = PositionVector2D((self.pos[0]+1, self.pos[1]+self.moving_direction))
                if new_pos[1] in (0, 7):
                    for letter in ("q", "r", "b", "n"):
                        yield Move(self.pos, new_pos, letter)
                else:
                    yield Move(self.pos, new_pos, None)
        except IndexError:
            pass

        try:
            if self.board.board[self.pos[1]+self.moving_direction][self.pos[0]-1] != 0:
                new_pos = PositionVector2D((self.pos[0]-1, self.pos[1]+self.moving_direction))
                if new_pos[1] in (0, 7):
                    for letter in ("q", "r", "b", "n"):
                        yield Move(self.pos, new_pos, letter)
                else:
                    yield Move(self.pos, new_pos, None)
        except IndexError:
            pass

        # en_passant
        if self.board.possible_en_passant == (self.pos[0]-1, self.pos[1]+self.moving_direction) or self.board.possible_en_passant == (self.pos[0]+1, self.pos[1]+self.moving_direction):
            yield Move(self.pos, self.board.possible_en_passant, None)



