from position import PositionVector2D
# A file with errors. Quite self-explanatory
"""

"""

class ImpossibleMoveException(BaseException):
    """ An error for an impossible move input """
    def __init__(self, piece, reason, init_pos, new_pos):
        """ an initialization function

        :param piece: the piece with which the move was made
        :type piece: pieces.Piece

        :param reason: the text of the reasoning behind the error
        :type reason: str

        :param init_pos: the initial position of the piece before the move
        :type init_pos: position.PositionVector2D

        :param new_pos: the final position of the piece after the move
        :type new_pos: position.PositionVector2D
        """
        super(ImpossibleMoveException, self).__init__(f"\nPiece: {piece.name}\nReason: {reason}\nMove from ({init_pos.algebraic}) to ({new_pos.algebraic})")



class PieceColorException(BaseException):
    """ An Error called when the player plays out of his turn """
    def __init__(self, piece):
        """ An initialization function

        :param piece: the piece with which the move was made
        :type piece: pieces.Piece
        """
        super(PieceColorException, self).__init__(f"\nPiece: {piece.name}\nColor: {piece.color}\nPosition: {piece.pos.algebraic}")


class UnrecognisableMove(BaseException):
    """ An error for an unrecognisable move """
    def __init__(self, move):
        """ An initialization function

        :param move: the input for move inputted
        :type: Any
        """
        super(UnrecognisableMove, self).__init__(f"\nCan't recognise the move ({move})")


class UnderCheckException(BaseException):
    """ An error when attempted to move under a check """
    def __init__(self, move: str, king_pos: PositionVector2D):
        """ An initialization function

        :param move: the string version of the move made
        :type move: str

        :param king_pos: the position fo the king that's inder the check
        :type king_pos: position.PositionVector2D
        """
        super(UnderCheckException, self).__init__(f"\nCant move the piece ({move}) as the king is under check on {king_pos.algebraic}")


class JustError(BaseException):
    """ An error class for something completely strange and unexpected """
    def __init__(self):
        """ An initialization function """
        super(JustError, self).__init__(f"\nI dont know what to write in this case, so you have somewhere an unexpected error")