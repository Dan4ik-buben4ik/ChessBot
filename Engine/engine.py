import Chess_lib.MoveGenerator as MoveGen
from Chess_lib.util import TurnColor

from .util import TTFlag, TTEntree
from .evaluation import StaticEvaluation
import math

from .logger import SearchLogger, timer
from .move_ordering import order_moves


logger = SearchLogger()





# import random
# def _TESTEvaluation(position: Board):
#     return random.random() * random.randint(1, 3) * [1, -1][random.randint(0, 1)]

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
        color = 1 if board.turn == TurnColor.WHITE else -1
        if board.game_end_check()[0]:
            return StaticEvaluation.evaluate(board) * color

        if depth == 0:
            return self._QuiescenceSearch(board, -beta, -alpha) * color

        best = -math.inf
        best_move = None
        for move in order_moves(board, MoveGen.generate_legal_moves(board), entry_move):
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

    def _QuiescenceSearch(self, board, alpha, beta):
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

        color = 1 if board.turn == TurnColor.WHITE else -1
        best = -math.inf

        for move in order_moves(board, MoveGen.generate_quiescence_legal_moves(board), entry_move):
            # print(f"engine considers: {move} | depth: 0")
            logger.log_intro(move, 0)
            board.push(move)
            evaluation = StaticEvaluation.evaluate(board) * color
            # print(f"static evaluation for move {move} at depth 0: {evaluation * color}\n")
            logger.log_outro(evaluation * color)
            board.pop()

            best = max(best, evaluation)

            alpha = max(alpha, evaluation)
            if alpha >= beta:
                break

            # logger(move, evaluation, 0)

        return best

    @timer
    def generate(self):
        best_score = -math.inf
        best_move = None

        alpha = self.init_alpha
        beta = self.init_beta

        for move in MoveGen.generate_legal_moves(self.board):
            print(f"engine considers: {move} | depth: {self.depth}")
            logger.log_intro(move, self.depth)
            self.board.push(move)
            try:
                evaluation = -self._AlphaBetaSearch(self.board, -beta, -alpha, self.depth - 1)
            except BaseException as exp:
                print(logger.parent_path)
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

        logger.log_outro(best_score)


        return best_move

    def evaluate(self):
        color = 1 if self.board.turn == TurnColor.WHITE else -1
        try:
            return self._AlphaBetaSearch(self.board, self.init_alpha, self.init_beta, self.depth) * color

        except BaseException as exp:
            print(logger.parent_path)
            logger.view_dict()
            logger.view_dict()
            logger.view_dict()
            raise exp

