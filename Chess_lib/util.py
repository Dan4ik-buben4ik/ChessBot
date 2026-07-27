# Util file
# THis is the file with additional functions that are wide used across scripts
import enum


class TurnColor(enum.Enum):
    #TODO: change all color attributes to this. fen, piece, loader
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



class MoveType(enum.Enum):
    NORMAL = 0
    CAPTURE = 1
    EN_PASSANT = 2
    CASTLE = 3

