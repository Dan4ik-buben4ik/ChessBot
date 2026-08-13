from Chess_lib.position import PositionVector2D
from Chess_lib import TurnColor

from util import *


def position_vector_converter(pos: PositionVector2D):
    return getattr(Square, pos.algebraic.upper())

def turn_color_converter(turn_color: TurnColor):
    return Color.WHITE if turn_color == 0 else Color.BLACK




