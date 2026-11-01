# This is a chess library for the creation of board instances for the games

# metadata
__version__ = "1.0.0"
__author__ = "Daniel Rakhmatov, Peter Luo"


from .loader import Board
from .util import *

__all__ = [
    "Board",
    "Color",
    "PieceType",
    "Square",
    "File",
    "Move"
]
