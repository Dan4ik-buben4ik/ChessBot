import MoveGenerator as MoveGen

from util import TurnColor
from evaluation import StaticEvaluation
import math


def AlphaBetaSearch(board, alpha, beta, depth):
    # depth 1 yields a -value for some reason
    #alpha = lower
    #beta = upper
    color = 1 if board.turn == TurnColor.WHITE else -1
    if board.game_end_check()[0]:
        return StaticEvaluation.evaluate(board) * color

    if depth == 0:
        return -QuiescenceSearch(board, -beta, -alpha)

    best = -math.inf
    for move in MoveGen.generate_legal_moves(board):
        print(f"engine considers: {move} | depth: {depth}")
        logger.log_intro(move, depth)
        board.push(move)
        evaluation = AlphaBetaSearch(board, -beta, -alpha, depth-1) * color

        print(f"static evaluation for move {move} at depth {depth}: {evaluation * color}\n")
        logger.log_outro(evaluation)
        board.pop()

        best = max(best, evaluation)

        alpha = max(alpha, evaluation)

        if alpha >= beta:
            break


        # logger(move, evaluation, depth)


    return best


def QuiescenceSearch(board, alpha, beta):
    color = 1 if board.turn == TurnColor.WHITE else -1
    best = -math.inf

    for move in MoveGen.generate_quiescence_legal_moves(board):
        print(f"engine considers: {move} | depth: 0")
        logger.log_intro(move, 0)
        board.push(move)
        evaluation = StaticEvaluation.evaluate(board) * color
        print(f"static evaluation for move {move} at depth 0: {evaluation * color}\n")
        logger.log_outro(evaluation)
        board.pop()


        best = max(best, evaluation)

        alpha = max(alpha, evaluation)
        if alpha >= beta:
            break


        # logger(move, evaluation, 0)

    return best



# import random
# def _TESTEvaluation(position: Board):
#     return random.random() * random.randint(1, 3) * [1, -1][random.randint(0, 1)]

class Engine:
    def __init__(self, board, alpha, beta, depth):
        self.board = board
        self.init_alpha = alpha
        self.init_beta = beta
        self.depth = depth

    def generate(self):
        color = 1 if self.board.turn == TurnColor.WHITE else -1
        best_score = -math.inf
        best_move = None

        alpha = self.init_alpha
        beta = self.init_beta

        for move in MoveGen.generate_legal_moves(self.board):
            print(f"engine considers: {move} | depth: {self.depth}")
            logger.log_intro(move, self.depth)
            self.board.push(move)
            evaluation = AlphaBetaSearch(self.board, -beta, -alpha, self.depth - 1) * color
            print(f"static evaluation for move {move} at depth {self.depth}: {evaluation * color}\n")
            self.board.pop()
            logger.log_outro(evaluation)


            if evaluation > best_score:
                best_score = evaluation
                best_move = move

            alpha = max(alpha, evaluation)




        return best_move

    def evaluate(self):
        color = 1 if self.board.turn == TurnColor.WHITE else -1
        try:
            return AlphaBetaSearch(self.board, self.init_alpha, self.init_beta, self.depth) * color
        except BaseException as exp:
            self.board.construct()
            raise exp


# class logger:
#     data = {}
#     chain = []
#     working_dict = data
#     @classmethod
#     def log(cls, move, evaluation, depth):
#         cls.working_dict[move] = {"evaluation": evaluation, "depth": depth}
#         cls.working_dict = cls.working_dict[move]
#         cls.append_chain(move)
#
#     @classmethod
#     def append_chain(cls, move):
#         cls.chain.append(move)
#
#     @classmethod
#     def pop_chain(cls):
#         cls.chain.pop()


import json
class logger:
    data = {
        "root": {"moves": [], "evaluation": 0, "depth": 0}
    }
    parent_path = "root"

    @classmethod
    def log_intro(cls, move, depth):
        new_path = f"{cls.parent_path}/{move.to_uci()}"
        cls.data[cls.parent_path]["moves"].append(move.to_uci())
        cls.data[cls.parent_path]["depth"] = depth
        cls.parent_path = new_path

        cls.data[new_path] = {"moves": [], "evaluation": 0, "depth": 0}

    @classmethod
    def log_outro(cls, evaluation):
        new_path = "/".join(cls.parent_path.split("/")[:-1])
        cls.data[cls.parent_path]["evaluation"] = evaluation
        cls.parent_path = new_path

    @classmethod
    def print_dict(cls):
        with open("log.json", "w", encoding="utf-8") as file:
            json.dump(cls.data, file, ensure_ascii=False)
            file.write("\n")
            file.flush()
        print(json.dumps(cls.data, indent=4))




# import json, sys
# sys.setrecursionlimit(10000)
# def print_dict(dictionary):
#     with open("log.json", "w", encoding="utf-8") as file:
#         json.dump(dictionary, file, indent=4, ensure_ascii=False)
#     # print(json.dumps(dictionary, indent=4))
