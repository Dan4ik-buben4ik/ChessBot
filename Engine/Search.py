from Chess_lib import *
import Chess_lib.MoveGenerator as MoveGen
import math


# #
# class AlphaBetaSearcher:
#     #TODO: change the bounds
#     ALPHA = -100 # eg
#     BETA = 100 #eg
#     def __init__(self, board: Board):
#         self.board = board
#
#     def search(self, depth):
#         """return best move and its evaluation
#         like [(move, eval)]
#         """
#         if depth == 0:
#             pass
#
#         # best_move = None
#         # best_score = -math.inf
#         current_turn = self.board.turn
#         for move in MoveGen.get_all_possible_moves(self.board):
#             self.board.push(move)
#             evaluation = TESTEvaluation(self.board)
#
#             if current_turn.name == "White":
#                 if evaluation >= self.BETA:
#                     break
#
#                 self.ALPHA = max(self.ALPHA, evaluation)
#                 return evaluation
#             else:
#
#                 if evaluation < self.ALPHA:
#                     break
#
#                 self.BETA = min(self.BETA, evaluation)
#                 return evaluation
#
#             self.board.pop()
#
#
#
#
#         return best_moves


def AlphaBetaSearch(board: Board, alpha, beta, depth):
    #alpha = lower
    #beta = upper
    color = 1 if board.turn.name == "WHITE" else -1
    if board.game_end_check()[0]:
        return TESTEvaluation(board) * color
    
    if depth == 0:
        return -QuiescenceSearch(board, -beta, -alpha)

    best = -math.inf
    for move in MoveGen.generate_legal_moves(board):
        board.push(move)
        evaluation = -AlphaBetaSearch(board, -beta, -alpha, depth-1)
        board.pop()

        best = max(best, evaluation)

        alpha = max(alpha, evaluation)

        if alpha >= beta:
            break


    return best


def QuiescenceSearch(board, alpha, beta):
    # TODO: add the evaluation function
    color = 1 if board.turn.name == "WHITE" else -1
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