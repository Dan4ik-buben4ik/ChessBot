from Chess_lib import *
from Chess_lib.util import *
from Chess_lib.nn import *
from Chess_lib.nn_maths import *
from Chess_lib.engine import Engine, logger


# only queens and kings: "3qk3/8/8/8/8/8/8/3QK3 w - - 0 1"
# only rooks and kings: r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1  hash = 8443997070231762362
# only bishops and kings: 2b1kb2/8/8/8/8/8/8/2B1KB2 w - - 0 1
# only knights and kings:1n2k1n1/8/8/8/8/8/8/1N2K1N1 w - - 0 1
# en_passant check: "4k3/8/8/8/1p6/8/P7/4K3 w - - 0 1"
# discovered-check check: 4k3/8/8/8/8/5p2/4P3/K3R3 w - - 0 1
# double check: "8/8/8/8/4k3/5p2/4P3/K3R3 w - - 0 1"
# all pawns on the last row: "2R5/PPPPPPPP/8/8/8/8/8/k6K w - - 0 1"
# starting position: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# diagonal pin : "4k3/8/8/8/7q/8/5N2/4K3 w KQkq - 0 1"
# empty : "8/8/8/8/8/8/8/8 w - - 0 1"

# bit_board = Board.from_fen("3k3r3/8/8/8/8/8/8/R3K3 w - - 0 1")
# bit_board.construct()
#
# # PLAN
# # - half kp set up
# # - pgn
#
#
#
# while True:
#     legal = list(bit_board.generate_legal_moves())
#     print("possible moves")
#     print(legal)
#
#     move = bit_board.parse_san(input("san: "))
#     bit_board.push(move)
#     bit_board.construct()
#     print(bit_board.outcome())


bit_board = Board.from_fen("r2k4/8/8/8/8/8/8/R3K3 b - - 0 1")
engine = Engine(bit_board, 100, -100, 10)

best_move = engine.generate()
print("best move")
print(best_move)
# print(len(logger.data.keys()))






