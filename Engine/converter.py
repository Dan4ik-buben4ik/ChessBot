from util import *


def position_vector_converter(pos):
    return getattr(Square, pos.algebraic.upper())

def turn_color_converter(turn_color):
    return Color.WHITE if turn_color == 0 else Color.BLACK




