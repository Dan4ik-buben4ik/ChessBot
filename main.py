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
 - prepare training environment
 - prep for error conditions
 IDEA: 
 - make the array value type a global variable
 - INceremental engine class decorator that wraps around all of the fuction and cuases them to check the clock first. 
 - Via while loop dfs?
"""

from Chess_lib import *
from Chess_lib.engine import *
import csv
import requests



ENGINE_POST = "https://chess-api.com/v1"
ENGINE_HEADER = {
    "Content-Type": "application/json"
}

FEN_INDEX = 1
SOLUTION_INDEX = 2
RATING_INDEX = 3

ENGINE_PATH = "nn_version_001.nnue"
PAWN_CNN_PATH = "pawn_cnn_version_001.nnue"
engine_mock = EvaluationNNUE()
engine_mock.to_file(ENGINE_PATH)

PawnStructCNN.to_file(PAWN_CNN_PATH)


def train(min_r=1000, max_r=2000, positions_num=10, learning_rate=0.001):
    engine = EvaluationNNUE()
    engine.from_file(ENGINE_PATH)
    PawnStructCNN.from_file(PAWN_CNN_PATH)
    errors = []
    with open("chessData.csv", "r") as puzzles:
        puzzle_reader = csv.reader(puzzles, delimiter=",")

        for index, puzzle in enumerate(puzzle_reader):
            if index == 0:
                continue

            if index == positions_num+1:
                break

            print(f"position unumber {index}")
            fen = puzzle[0]
            if puzzle[1].startswith("#"):  # a checkmate position, so I need searcher for it, which I dont use now
                continue
            expected_eval = np.float32(int(puzzle[1]) / 100)
            board = Board.from_fen(fen)


            # payload = {"fen": board.to_fen()}

            # expected_move, expected_eval = send_request(payload)


            # pred_move, pred_evaluation = incremental_evaluation(board, engine, expected_eval-10000, expected_eval+10000, 10)
            input_vector = engine.build_input(board)
            pred_evaluation = engine.forward(input_vector)
            # pred_evaluation /= 100

            error = squared_error_loss_prime(pred_evaluation, expected_eval)
            assert np.isfinite(error)

            errors.append(squared_error_loss(pred_evaluation, expected_eval))

            # print(f"best move: {expected_move} | match = {expected_move == pred_move.uci()}")
            print(f"stockfish eval: {expected_eval} | Prediction: {pred_evaluation} | error {squared_error_loss(pred_evaluation, expected_eval)}")


            grad = np.array(error).reshape((1, 1)).astype(np.float32)


            engine.back_propagation(grad, learning_rate, board)

            engine.to_file(ENGINE_PATH)
            PawnStructCNN.to_file(PAWN_CNN_PATH)
            print("no issues with paths")
        return errors






def send_request(payload):
    """
    Gets the best move and evaluation from the https://chess-api.com/v1 endpoint
    :param payload: the metadata send by the request
    :return: best move, evaluation
    """
    while True:
        try:
            result = requests.post(ENGINE_POST, headers=ENGINE_HEADER, json=payload)
            if result.status_code == 200:
                data = result.json()
                if data.get('type') == 'info':
                    print(f"API Info Message: {data.get('text')}")
                move = data.get('move')
                eval = data.get('eval')
                print(f"move: {move}")
                print(f"eval: {eval}")
                if move is None or eval is None:
                    raise requests.exceptions.RequestException
                return move, eval
            else:
                print(f"API error. Status Code: {result.status_code}")
                print(result.text)
        except requests.exceptions.RequestException as e:
            print(f"error occured {e}")

# training_num = 5000
# error_arr = train(1000, 2000, training_num, 0.00001)
# print(error_arr)
# print("mean error")
# print(np.sum(error_arr)/training_num)
# # PawnStructCNN.to_file("pawn_cnn_version_001.nnue")




