ChessBot - A Neural Chess Engine

# Overview

This is a still work in progress project, but it already has the basic engine created and currently trained. The engine uses Alpha-Beta Search, along with NNUE evaluation via Half KA and a pawn structure cnn.

Current State: NN training

# Future Plans
IN future, planned to use batched gpu computations. Currently, the batching system is finished in the Dan branch, but needs more debugging and polishing before commiting


# Setup Example
``` Python
import Chess_lib
import Chess_lib.engine
from Chess_lib.nn import init_engine

import time

#initialising
board = Chess_lib.Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
engine = init_engine()

#evaluating
start = time.time()
move, evaluation, logger = Chess_lib.engine.evaluate(board, engine, -100, 100, 5)
end = time.time()


time_taken = end - start

print(move.uci(), evaluation)
print(f"Best move: {move.uci()}")
print(f"Position evaluation: {evaluation}")
print(f"Nodes checked: {logger.nodes}")
print(f"Time taken: {time_taken:2g}")
print(f"NPS = {(logger.nodes /time_taken):.2g}")

#pushing move
board.push(move)
board.construct()

#generating legal moves
print("legal moves")
print(list(board.generate_legal_moves()))

#popping a move
board.pop()
```
