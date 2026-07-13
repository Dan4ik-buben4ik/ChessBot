# Util file
# THis is the file with additional functions that are wide used across scripts
from _enum import BaseEnum, EnumValues



class Color(BaseEnum):
    WHITE = 0
    BLACK = 1

    def next(self):
        return self._next

    @property
    def opposite(self):
        return self.next()

