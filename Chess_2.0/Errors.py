from util import pos_to_cord
from position import PositionVector2D
# A file with errors. Quite self-explanatory

class ImpossibleMoveException(BaseException):
    def __init__(self, piece, reason, init_pos, new_pos):
        super(ImpossibleMoveException, self).__init__(f"\nPiece: {piece.name}\nReason: {reason}\nMove from ({PositionVector2D.pos_to_cord(init_pos)}) to ({pos_to_cord(new_pos)})")



class PieceColorException(BaseException):
    def __init__(self, piece):
        super(PieceColorException, self).__init__(f"\nPiece: {piece.name}\nColor: {piece.color}\nPosition: {PositionVector2D.pos_to_cord(piece.pos)}")


class UnrecognisableMove(BaseException):
    def __init__(self, move):
        super(UnrecognisableMove, self).__init__(f"\nCan't recognise the move ({move})")


class JustError(BaseException):
    def __init__(self):
        super(JustError, self).__init__(f"\nI dont know what to write in this case, so you have somewhere an unexpected error")