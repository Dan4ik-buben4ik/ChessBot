from loader import Board
import MoveGenerator as MoveGen
from util import TurnColor
import math


def AlphaBetaSearch(board: Board, alpha, beta, depth):
    #alpha = lower
    #beta = upper
    color = 1 if board.turn == TurnColor.WHITE else -1
    if board.game_end_check()[0]:
        return TESTEvaluation(board) * color

    if depth == 0:
        return -QuiescenceSearch(board, -beta, -alpha)

    best = -math.inf
    for move in MoveGen.generate_legal_moves(board):
        board.push(move)
        evaluation = AlphaBetaSearch(board, -beta, -alpha, depth-1) * color
        board.pop()

        best = max(best, evaluation)

        alpha = max(alpha, evaluation)

        if alpha >= beta:
            break


    return best


def QuiescenceSearch(board, alpha, beta):
    # TODO: add the evaluation function
    color = 1 if board.turn == TurnColor.WHITE else -1
    best = -math.inf

    for move in MoveGen.generate_quiescence_legal_moves(board):
        board.push(move)
        evaluation = TESTEvaluation(board) * color
        board.pop()

        best = max(best, evaluation)

        alpha = max(alpha, evaluation)
        if alpha >= beta:
            break

    return best



import random
def TESTEvaluation(position: Board):
    return random.random() * random.randint(1, 3) * [1, -1][random.randint(0, 1)]