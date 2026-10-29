from Chess_lib import *
from Chess_lib.util import *
from Chess_lib.nn import *
from Chess_lib.nn_maths import *
from Chess_lib.engine import *


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

#
""" 
PLAN:
- if checkmate, return inf val or 0 if draw
- account for the error, and save the weights
- Prep the model for back propagation
 - start training model
 
 
 
 
 
 - think of GAB?
  - Work on GPU NN evaluation
 - look for ways to optimise (aka the dfs batching and gpu batching - maybe incremental batching? )
 - connect gpu to the searcher.
 
 IDEA (for after the GPU code)
 - Geometric Attention Bias for move ordering
 - Uses the GAB for a pure policy (gives % prob to all moves) every n nodes (3 but decide later via testing)
 - This could speed the search and lessen the number of nodes searching
 LIMITATION
 - Can cause the GPU resource sharing issue
 - would only be called n moves, before the gpu starts evaluating. THen locks and blocks any requests (checkable before sending requests)
 - Issue with incremental depth
 
*** Start writing docs for finished functions
"""

from Chess_lib import *
from Chess_lib.engine import *
import numpy as np
import numpy.random

import time


# board = Board.from_fen("7k/Q7/8/8/8/8/8/4K3 w - - 0 1")
# board.construct()
#
# move = Move.from_uci(input("move: "))
# board.push(move)
#
# start = time.time()
# asyncio.run(evaluate(board, -1000, 1000, 2))
# end = time.time()
# print(f"took {end-start:.2f} sec")

# res = EvaluationNNUE.forward(np.zeros(EvaluationNNUE.input_shape))
# print(res)
#
# grad = np.array([10])
# learning_rate = 0.1
# EvaluationNNUE.back_propagation(grad, learning_rate)
# # test that the back prop works



