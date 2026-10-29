import numpy as np
import asyncio
import csv
import requests

from Chess_lib import *
from Chess_lib.engine import *
from Chess_lib.util import *
from Chess_lib.nn import *


# async def main():
#     # 1) get position
#     active_board = Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
#
#     # 2) best move
#     best_move = await best_move_cpu(active_board, 7)
#
#
# asyncio.run(main())

ENGINE_POST = "https://chess-api.com/v1"
ENGINE_HEADER = {
    "Content-Type": "application/json"
}

FEN_INDEX = 1
SOLUTION_INDEX = 2
RATING_INDEX = 3

async def train(min_r=1000, max_r=2000, learning_rate=0.001):
    with open("example.csv", "r") as puzzles:
        puzzle_reader = csv.reader(puzzles, delimiter=",")
        for index, puzzle in enumerate(puzzle_reader):
            if index == 0:
                continue
            if index != 1:
                continue
            fen = puzzle[FEN_INDEX]
            solution_seq = map(lambda x: Move.from_uci(x), puzzle[SOLUTION_INDEX].split(" "))
            rating = int(puzzle[RATING_INDEX])
            # rating filter
            if not (min_r < rating < max_r):
                continue

            board = Board.from_fen(fen)

            puzzle_error = 0
            while True:
                next_move = next(solution_seq, None)
                if next_move is None:
                    break

                payload = {"fen": board.to_fen()}

                expected_move, expected_eval = send_request(payload)

                pred_move, pred_evaluation = await best_move_cpu(board, 2)
                pred_evaluation /= 100

                local_error = squared_error_loss(pred_evaluation, expected_eval)
                puzzle_error += local_error

                print(type(pred_move))
                print(f"best move: {expected_move} | match = {expected_move == pred_move.uci()}")
                print(f"stockfish eval: {expected_eval} | error {local_error}")
                return

            grad = np.array(puzzle_error).reshape((1, 1))

            print(f"total puzzle error: {grad}")

            EvaluationNNUE.back_propagation(grad, learning_rate, board)




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
                print(f"move: {data.get('move')}")
                print(f"eval: {data.get('eval')}")
                return data.get('move'), data.get('eval')
            else:
                print(f"API error. Status Code: {result.status_code}")
                print(result.text)
        except requests.exceptions.RequestException as e:
            print(f"error occured {e}")


asyncio.run(train(1000, 2000, 0.0001))