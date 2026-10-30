import math
from typing import TypeAlias
import enum

from .util import *
from .loader import Board
from .nn import *


# Material: TypeAlias = int
# #all in centipawns
# PAWN_MATERIAL: Material = 100
# KNIGHT_MATERIAL: Material = 300
# BISHOP_MATERIAL: Material = 300
# ROOK_MATERIAL: Material = 500
# QUEEN_MATERIAL: Material = 900
#
# PieceSquareTable: TypeAlias = list
# KNIGHT_PST: PieceSquareTable = [
#     -5, -4, -3, -2, -2, -3, -4, -5,
#     -4, -2,  0,  1,  1,  0, -2, -4,
#     -3,  0,  2,  3,  3,  2,  0, -3,
#     -2,  1,  3,  4,  4,  3,  1, -2,
#     -2,  1,  3,  4,  4,  3,  1, -2,
#     -3,  0,  2,  3,  3,  2,  0, -3,
#     -4, -2,  0,  1,  1,  0, -2, -4,
#     -5, -4, -3, -2, -2, -3, -4, -5
# ]
#
# BISHOP_PST = [
#     -3, -2, -1, -1, -1, -1, -2, -3,
#     -2, -1,  0,  1,  1,  0, -1, -2,
#     -1,  0,  1,  2,  2,  1,  0, -1,
#      0,  1,  3,  4,  4,  3,  1,  0,
#      0,  1,  3,  4,  4,  3,  1,  0,
#     -1,  0,  1,  2,  2,  1,  0, -1,
#     -2, -1,  0,  1,  1,  0, -1, -2,
#     -3, -2, -1, -1, -1, -1, -2, -3
# ]
#
# ROOK_PST = [
#      5,  5,  5,  5,  5,  5,  5,  5,
#     20, 20, 20, 20, 20, 20, 20, 20,
#      0,  0,  0,  5,  5,  0,  0,  0,
#      0,  0,  0,  5,  5,  0,  0,  0,
#      0,  0,  0,  5,  5,  0,  0,  0,
#      0,  0,  0,  5,  5,  0,  0,  0,
#     15, 15, 15, 15, 15, 15, 15, 15,
#      5,  5,  5,  5,  5,  5,  5,  5
# ]
#
# QUEEN_PST = [
#     -3, -2, -1, -1, -1, -1, -2, -3,
#     -2, -1,  0,  1,  1,  0, -1, -2,
#     -1,  0,  1,  2,  2,  1,  0, -1,
#      0,  1,  3,  4,  4,  3,  1,  0,
#      0,  1,  3,  4,  4,  3,  1,  0,
#     -1,  0,  1,  2,  2,  1,  0, -1,
#     -2, -1,  0,  1,  1,  0, -1, -2,
#     -3, -2, -1, -1, -1, -1, -2, -3
# ]
#
# KING_OPENING_PST = [
#      5,  4,  3,  0,  1,  2,  4,  5,
#      1,  0, -1, -1, -1, -1,  0,  1,
#     -1, -2, -3, -4, -4, -3, -2, -1,
#     -2, -3, -4, -5, -5, -4, -3, -2,
#     -2, -3, -4, -5, -5, -4, -3, -2,
#     -1, -2, -3, -4, -4, -3, -2, -1,
#      1,  0, -1, -1, -1, -1,  0,  1,
#      5,  4,  3,  0,  1,  2,  4,  5,
# ]
#
# KING_ENDGAME_PST = [
#     -3, -2, -1, -1, -1, -1, -2, -3,
#     -2, -1,  0,  1,  1,  0, -1, -2,
#     -1,  0,  1,  2,  2,  1,  0, -1,
#      0,  1,  3,  4,  4,  3,  1,  0,
#      0,  1,  3,  4,  4,  3,  1,  0,
#     -1,  0,  1,  2,  2,  1,  0, -1,
#     -2, -1,  0,  1,  1,  0, -1, -2,
#     -3, -2, -1, -1, -1, -1, -2, -3
# ]
#
#
#
# bishop_pair = 30
# doubled_pawn = - 15
# isolated_pawn = -20
# passed_pawn = 45
# mobility = 3
# activity_scale = 0.02
# king_open_file = -50
# rook_open_file = 20
# tempo = 10

#transposition table flags
TTFlag: TypeAlias = int
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

    if board.is_move_check(move): # TODO: make lazy, so no push/pop
        score += 5

    if board.is_capture(move):
        score += 3

    if move.promotion:
        score += 2

    return score



def move_ordering(board: Board, moves: list[Move], tt_move=None):
    yield from sorted(
        moves,
        key=lambda x: _move_order_score(board, x, tt_move),
        reverse=True
    )






class SearchLogger:
    data = {
        "root": {"moves": [], "move evaluations": [], "evaluation": 0, "depth": 0}
    }
    nodes = 0


    def log_intro(self, root, move: str, depth):
        self.nodes += 1
        new_path = f"{root}/{move}"
        self.data[root]["moves"].append(move)
        self.data[root]["depth"] = depth

        self.data[new_path] = {"moves": [], "move evaluations": [], "evaluation": 0, "depth": 0}
        return new_path

    def log_outro(self, path, evaluation):
        new_path = "/".join(path.split("/")[:-1])
        self.data[path]["evaluation"] = evaluation
        if new_path:
            self.data[new_path]["move evaluations"].append(evaluation)


    def print_dict(self):
        with open("log.txt", "w", encoding="utf-8") as file:
            import json
            file.write(json.dumps(self.data, indent=4))
            file.write("\n")
            file.flush()
        # print(json.dumps(self.data, indent=4))

    def view_dict(self):
        try:
            path = input("\nInput the path to check the values: ")
            temp = self.data[path]
            print(f"path: {path}")
            print(f"moves: {temp['moves']}")
            print(f"path evaluation: {temp['evaluation']}")
            print(f"move evaluations: {temp['move evaluations']}")
            print(f"depth: {temp['depth']}")
        except BaseException:
            print("There is no such path")


def search(board, alpha, beta, depth, boundary, tt, *, logger: SearchLogger, root: str="root"):
    color = 1 if board.turn == WHITE else -1
    outcome = board.outcome()
    print(outcome)
    if outcome == GameResult.CHECKMATE:
        return INF * color
    elif outcome != GameResult.ONGOING:
        return 0

    entry_move = None
    # checks if the position had already been analysed.
    entry = tt.get(board.hash)
    if entry and entry.depth >= depth:
        print(entry.depth, depth, entry.depth >= depth)
        entry_move = entry.best_move

        if entry.flag == EXACT:
            return entry.score
        elif entry.flag == LOWER_BOUND:
            alpha = max(alpha, entry.score)
        elif entry.flag == UPPER_BOUND:
            beta = min(beta, entry.score)

        if alpha > beta:
            return entry.score

    # sets up the variables needed post evaluation
    original_alpha = alpha
    original_beta = beta

    if board.outcome() != GameResult.ONGOING:
        input_vector = EvaluationNNUE.build_input(board)
        return EvaluationNNUE.forward(input_vector) * color
    print(f"Searching at depth ({depth}) with boundary: {boundary}")

    best_move = None
    best = -INF
    for move in move_ordering(board, list(board.generate_legal_moves()), entry_move):
        print(f"depth {depth} move ({move.uci()})")
        print()
        board.push(move)

        if depth >= boundary:
            print("hit boundary")
            input_vector = EvaluationNNUE.build_input(board)
            evaluation = EvaluationNNUE.forward(input_vector).item()

        else:
            print("searching deeper")
            branch = logger.log_intro(root, move.uci(), depth)
            evaluation = -search(board, -beta, -alpha, depth+1, boundary, tt, logger=logger, root=branch)
        board.pop()

        if evaluation > best:
            best = evaluation
            best_move = move

        alpha = max(alpha, best)
        if alpha >= beta:
            break

    logger.log_outro(root, best)

    # records the position into the table
    if best <= original_alpha:
        flag = UPPER_BOUND
    elif best >= original_beta:
        flag = LOWER_BOUND
    else:
        flag = EXACT

    tt[board.hash] = TTEntree(depth, best, flag, best_move.uci())

    return best



def evaluate(board, alpha, beta, boundary_depth, *, debug=False):
    transposition_table = {}

    color = 1 if board.turn == WHITE else -1
    temp_board = Board()
    temp_board.copy_from(board)
    logger = SearchLogger()
    res = search(board, alpha, beta, 1, boundary_depth, transposition_table, logger=logger)
    best_move = None
    entree = transposition_table.get(board.hash, None)
    if entree:
        best_move = entree.best_move
    print(f"result = {res}")
    print(f"best move: {best_move}")
    print(f"Positions: {logger.nodes}")
    # for _ in range(5):
    #     logger.view_dict()
    return best_move, res

def incremental_evaluation(board, alpha, beta, time_out):
    try:
        import time
    except ImportError:
        pass

    start = time.time()
    best_move = None
    res = 0
    for d in range(1, 100):
        res, best_move = evaluate(board, alpha, beta, d)

        end = time.time()
        if end - start >= time_out:
            print(f"max depth reached {d}")
            break
    else:
        print("reached depth of 100+")
    print(f"result = {res}")
    print(f"best move: {best_move}")

    return res, best_move
