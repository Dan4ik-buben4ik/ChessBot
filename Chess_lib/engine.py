import dataclasses
import math
from typing import TypeAlias

from .util import *
from .loader import Board
from .logger import *
from .nn import *


Material: TypeAlias = int
#all in centipawns
PAWN_MATERIAL: Material = 100
KNIGHT_MATERIAL: Material = 300
BISHOP_MATERIAL: Material = 300
ROOK_MATERIAL: Material = 500
QUEEN_MATERIAL: Material = 900

PieceSquareTable: TypeAlias = list
KNIGHT_PST: PieceSquareTable = [
    -5, -4, -3, -2, -2, -3, -4, -5,
    -4, -2,  0,  1,  1,  0, -2, -4,
    -3,  0,  2,  3,  3,  2,  0, -3,
    -2,  1,  3,  4,  4,  3,  1, -2,
    -2,  1,  3,  4,  4,  3,  1, -2,
    -3,  0,  2,  3,  3,  2,  0, -3,
    -4, -2,  0,  1,  1,  0, -2, -4,
    -5, -4, -3, -2, -2, -3, -4, -5
]

BISHOP_PST = [
    -3, -2, -1, -1, -1, -1, -2, -3,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -1,  0,  1,  2,  2,  1,  0, -1,
     0,  1,  3,  4,  4,  3,  1,  0,
     0,  1,  3,  4,  4,  3,  1,  0,
    -1,  0,  1,  2,  2,  1,  0, -1,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -3, -2, -1, -1, -1, -1, -2, -3
]

ROOK_PST = [
     5,  5,  5,  5,  5,  5,  5,  5,
    20, 20, 20, 20, 20, 20, 20, 20,
     0,  0,  0,  5,  5,  0,  0,  0,
     0,  0,  0,  5,  5,  0,  0,  0,
     0,  0,  0,  5,  5,  0,  0,  0,
     0,  0,  0,  5,  5,  0,  0,  0,
    15, 15, 15, 15, 15, 15, 15, 15,
     5,  5,  5,  5,  5,  5,  5,  5
]

QUEEN_PST = [
    -3, -2, -1, -1, -1, -1, -2, -3,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -1,  0,  1,  2,  2,  1,  0, -1,
     0,  1,  3,  4,  4,  3,  1,  0,
     0,  1,  3,  4,  4,  3,  1,  0,
    -1,  0,  1,  2,  2,  1,  0, -1,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -3, -2, -1, -1, -1, -1, -2, -3
]

KING_OPENING_PST = [
     5,  4,  3,  0,  1,  2,  4,  5,
     1,  0, -1, -1, -1, -1,  0,  1,
    -1, -2, -3, -4, -4, -3, -2, -1,
    -2, -3, -4, -5, -5, -4, -3, -2,
    -2, -3, -4, -5, -5, -4, -3, -2,
    -1, -2, -3, -4, -4, -3, -2, -1,
     1,  0, -1, -1, -1, -1,  0,  1,
     5,  4,  3,  0,  1,  2,  4,  5,
]

KING_ENDGAME_PST = [
    -3, -2, -1, -1, -1, -1, -2, -3,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -1,  0,  1,  2,  2,  1,  0, -1,
     0,  1,  3,  4,  4,  3,  1,  0,
     0,  1,  3,  4,  4,  3,  1,  0,
    -1,  0,  1,  2,  2,  1,  0, -1,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -3, -2, -1, -1, -1, -1, -2, -3
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

#transposition table
class TTFlag(enum.Enum):
    __slots__ = ()
    UPPER_BOUND = 0
    LOWER_BOUND = 1
    EXACT = 2


class TTEntree:
    __slots__ = ("depth", "score", "flag", "best_move",)

    def __init__(self, depth, score, flag, best_move):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move

def _move_order_score(board: Board, move: Move, tt_move=None):
    score = 0

    if move == tt_move:
        score += 10

    if board.is_move_check(move):
        score += 5

    if board.is_capture(move):
        score += 3

    if move.promotion:
        score += 2

    return score



def move_ordering(board: Board, moves: list[Move], tt_move=None):
    return sorted(
        moves,
        key=lambda x: _move_order_score(board, x, tt_move),
        reverse=True
    )



logger = SearchLogger()
class Engine:
    def __init__(self, board, alpha, beta, depth):
        self.board = board
        self.init_alpha = alpha
        self.init_beta = beta
        self.depth = depth
        self.transposition_table = {}

    def _AlphaBetaSearch(self, board, alpha, beta, depth):
        entry_move = None
        #checks if the position had already been analysed
        entry = self.transposition_table.get(board.hash)
        if entry and entry.depth >= depth:
            entry_move = entry.best_move

            if entry.flag == TTFlag.EXACT:
                return entry.score
            elif entry.flag == TTFlag.LOWER_BOUND:
                alpha = max(alpha, entry.score)
            elif entry.flag == TTFlag.UPPER_BOUND:
                beta = min(beta, entry.score)

            if alpha > beta:
                return entry.score


        original_alpha = alpha
        original_beta = beta
        color = 1 if board.turn == WHITE else -1
        if board.outcome() != GameResult.ONGOING:
            return EvaluationNNUE.forward(board)[0] * color

        if depth == 0:
            return self._QuiescenceSearch(board, -beta, -alpha) * color

        best = -math.inf
        best_move = None
        for move in move_ordering(board, list(board.generate_legal_moves()), entry_move):
            # print(f"engine considers: {move} | depth: {depth}")
            logger.log_intro(move, depth)
            board.push(move)

            evaluation = -self._AlphaBetaSearch(board, -beta, -alpha, depth - 1)

            # print(f"static evaluation for move {move} at depth {depth}: {evaluation}\n")
            logger.log_outro(evaluation)
            board.pop()

            if evaluation > best:
                best = evaluation
                best_move = move

            alpha = max(alpha, evaluation)

            if alpha >= beta:
                break

        #records the position into the table
        if best <= original_alpha:
            flag = TTFlag.UPPER_BOUND
        elif best >= original_beta:
            flag = TTFlag.LOWER_BOUND
        else:
            flag = TTFlag.EXACT

        self.transposition_table[board.hash] = TTEntree(depth, best, flag, best_move)

        return best

    def _QuiescenceSearch(self, board: Board, alpha, beta):
        entry_move = None
        entry = self.transposition_table.get(board.hash)
        if entry and entry.depth > 0:
            entry_move = entry.best_move

            if entry.flag == TTFlag.EXACT:
                return entry.score
            elif entry.flag == TTFlag.LOWER_BOUND:
                alpha = max(alpha, entry.score)
            elif entry.flag == TTFlag.UPPER_BOUND:
                beta = min(beta, entry.score)

            if alpha > beta:
                return entry.score

        color = 1 if board.turn == WHITE else -1
        best = -math.inf

        for move in move_ordering(board, list(board.generate_legal_moves()), entry_move):
            if board.is_capture(move) or board.is_move_check(move):
                continue
            print(f"engine considers: {move} | depth: 0")
            logger.log_intro(move, 0)
            board.push(move)
            evaluation = EvaluationNNUE.forward(board)[0] * color
            print(f"static evaluation for move {move} at depth 0: {evaluation * color}\n")
            logger.log_outro(evaluation * color)
            board.pop()

            best = max(best, evaluation)

            alpha = max(alpha, evaluation)
            if alpha >= beta:
                break

        return best

    @timer
    def generate(self):
        best_score = -math.inf
        best_move = None

        alpha = self.init_alpha
        beta = self.init_beta

        for move in self.board.generate_legal_moves():
            print(f"engine considers: {move} | depth: {self.depth}")
            logger.log_intro(move, self.depth)
            self.board.push(move)
            try:
                evaluation = -self._AlphaBetaSearch(self.board, -beta, -alpha, self.depth - 1)
            except BaseException as exp:
                print(logger.parent_path)
                raise exp
                logger.view_dict()
                logger.view_dict()
                logger.view_dict()
                raise exp
            print(f"static evaluation for move {move} at depth {self.depth}: {evaluation}\n")
            self.board.pop()
            logger.log_outro(evaluation)


            if evaluation > best_score:
                best_score = evaluation
                best_move = move

            alpha = max(alpha, evaluation)

        if best_score <= self.init_alpha:
            flag = TTFlag.UPPER_BOUND
        elif best_score >= self.init_beta:
            flag = TTFlag.LOWER_BOUND
        else:
            flag = TTFlag.EXACT

        self.transposition_table[self.board.hash] = TTEntree(self.depth, best_score, flag, best_move)

        return best_move

    def evaluate(self):
        color = 1 if self.board.turn == WHITE else -1
        return self._AlphaBetaSearch(self.board, self.init_alpha, self.init_beta, self.depth) * color
