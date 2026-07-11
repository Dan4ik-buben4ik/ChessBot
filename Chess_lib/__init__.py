# This is a chess library for the creation of board instances for the games

# metadata
__version__ = "1.0.0"
__author__ = "Daniel Rakhmatov, Peter Luo"

from loader import Board
from fen_converter import board_to_FEN, FEN_to_board, validate_FEN
from pieces import Pawn, Bishop, King, Rook, Queen, Knight, Piece
from position import PositionVector2D

__all__ = [
    "Board",
    "board_to_FEN",
    "FEN_to_board",
    "validate_FEN",
    "Piece",
    "Pawn",
    "Knight",
    "Bishop",
    "Rook",
    "Queen",
    "King",
    "PositionVector2D"
]
