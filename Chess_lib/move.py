from .util import *
from .error import *


FROM_OFFSET = 0
TO_OFFSET = 6
PROMOTION_OFFSET = 12

FROM_MASK = 0b111111
TO_MASK = 0b111111
PROMOTION_MASK = 0b111


class Move:
    __slots__ = ("value",)

    def __init__(self, from_square, to_square, promotion: PieceType = 0):
        self.value = (
            from_square << FROM_OFFSET |
            to_square << TO_OFFSET |
            promotion << PROMOTION_OFFSET
        )

    @property
    def from_square(self):
        return (self.value >> FROM_OFFSET) & FROM_MASK

    @property
    def to_square(self):
        return (self.value >> TO_OFFSET) & TO_MASK

    @property
    def promotion(self):
        return (self.value >> PROMOTION_OFFSET) & PROMOTION_MASK


    @classmethod
    def from_uci(cls, uci):
        if not (4 <= len(uci) <= 5):
            raise InvalidMoveException(f"Invalid uci {uci}")

        try:
            from_square = SQUARE_NAMES.index(uci[:2])
            to_square = SQUARE_NAMES.index(uci[2:4])
            promotion = PIECE_SYM.index(uci[4]) if len(uci) == 5 else 0
            return cls(from_square, to_square, promotion)
        except ValueError:
            raise InvalidMoveException(f"Invalid uci {uci}")

    def uci(self):
        if self.promotion:
            return SQUARE_NAMES[self.from_square] + SQUARE_NAMES[self.to_square] + PIECE_SYM[self.promotion]
        else:
            return SQUARE_NAMES[self.from_square] + SQUARE_NAMES[self.to_square]

    def __repr__(self):
        return self.uci()








