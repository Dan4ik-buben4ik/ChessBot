# Util file
# THis is the file with additional functions that are wide used across scripts
import enum
from dataclasses import dataclass


class TurnColor(enum.IntEnum):
    WHITE = 0
    BLACK = 1

    def next(self):
        members = list(self.__class__)
        index = members.index(self)

        next_index = (index + 1) % len(members)
        return members[next_index]

    def previous(self):
        members = list(self.__class__)
        index = members.index(self)

        next_index = (index - 1) % len(members)
        return members[next_index]


@dataclass
class EvalTable:
    #all in centipawns
    piece_value = {
        "Pawn": 100,
        "Knight": 300,
        "Bishop": 300,
        "Rook": 500,
        "Queen": 900,
    }

    activity = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 2, 2, 2, 2, 1, 0],
        [0, 1, 2, 4, 4, 2, 1, 0],
        [0, 1, 2, 4, 4, 2, 1, 0],
        [0, 1, 2, 2, 2, 2, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    bishop_pair = 30
    doubled_pawn = - 15
    isolated_pawn = -20
    passed_pawn = 45
    mobility = 3
    activity_scale = 0.02
    king_open_file = -50
    rook_open_file = 20
    tempo = 10


