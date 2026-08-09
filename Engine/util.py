import enum


class TTFlag(enum.Enum):
    UPPER_BOUND = 0
    LOWER_BOUND = 1
    EXACT = 2


class TTEntree:
    def __init__(self, depth, score, flag, best_move):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move