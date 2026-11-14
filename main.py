import Chess_lib
import Chess_lib.engine
from Chess_lib.nn import init_engine

import time

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

board = Chess_lib.Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
engine = init_engine()

import cProfile, pstats

profiler = cProfile.Profile()


start = time.time()
profiler.enable()
move, evaluation, logger = Chess_lib.engine.evaluate(board, engine, -100, 100, 5)
profiler.disable()
end = time.time()

stats = pstats.Stats(profiler).sort_stats('tottime')
stats.print_stats(15)


time_taken = end - start

print(move.uci(), evaluation)
print(f"Best move: {move.uci()}")
print(f"Position evaluation: {evaluation}")
print(f"Nodes checked: {logger.nodes}")
print(f"Time taken: {time_taken:2g}")
print(f"NPS = {(logger.nodes /time_taken):.2g}")
#
# board.push(move)
# board.construct()
#
# print("legal moves")
# print(list(board.generate_legal_moves()))