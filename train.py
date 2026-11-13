from Chess_lib import *
from Chess_lib.util import *
from Chess_lib.nn import *
from Chess_lib.nn_maths import *
from Chess_lib.engine import *
from Chess_lib.file_formats import ExitPreventionLock

import csv
from pathlib import Path

PUZZLE_PATH = Path(__file__).resolve().parent / "TrainingData" / "lichess_db_puzzle.csv"


def position_generator(file_path, exclude_mates=True):
    with open(file_path, "r") as puzzles:
        puzzle_reader = csv.reader(puzzles, delimiter=",")
        next(puzzle_reader)
        for pos in puzzle_reader:
            fen = pos[0]
            if exclude_mates and pos[1].startswith("#"):  # a checkmate position, so I need searcher for it, which I dont use now
                continue

            target = cp_to_target(int(pos[1]))
            # target = scale(int(pos[1]))
            yield fen, target

def train(engine: EvaluationNNUE, datafile, positions_num=-1, learning_rate=0.001, save_cycle=1000):
    if not isinstance(datafile, Path):
        raise

    white_mae = 0
    black_mae = 0
    white_cp_mae = 0
    black_cp_mae = 0


    black_count = 0
    white_count = 0

    abs_error = 0


    count = 0
    for fen, target in position_generator(datafile):
        if count == positions_num:  # checks if we have checked the position_num positions
            break
        count += 1

        board = Board.from_fen(fen)


        input_vector = engine.build_input(board)
        prediction = engine.forward(input_vector, cp=False)
        prediction = prediction.item()

        # print(alpha * np.sinh(alpha * (pred_evaluation - target)))
        error = squared_error_loss_prime(prediction, target)
        print(error)
        assert np.isfinite(error)

        cp_diff = abs(target_to_cp(target) - target_to_cp(prediction))  # potential experiments with scalers
        ev_diff = abs(target - prediction)


        if target < 0:
            black_count += 1
            black_mae += ev_diff
            black_cp_mae += cp_diff
        elif target > 0:
            white_count += 1
            white_mae += ev_diff
            white_cp_mae += cp_diff


        print("Back propagation")
        grad = np.array(error).reshape((1, 1)).astype(np.float32)
        engine.back_propagation(grad, learning_rate, board)
        print(f"Position number: {count} | stockfish target: {target} | Prediction: {prediction} | error {squared_error_loss(prediction, target)}")

        if count % save_cycle == 0:
            engine.to_file(ENGINE_WEIGHTS_PATH)
            PawnStructCNN.to_file(PAWN_CNN_WEIGHTS_PATH)

    return count, abs_error / count, white_count, white_mae, white_cp_mae, black_count, black_mae, black_cp_mae


def assess(engine, access_file_path, positions_num=-1, engine_depth=10):
    if not isinstance(access_file_path, Path):
        raise BaseException

    correct_puzzles = 0
    total_puzzles = 0

    with open(access_file_path, "r") as puzzles:
        puzzle_reader = csv.reader(puzzles, delimiter=",")

        for index, puzzle in enumerate(puzzle_reader):
            fen = puzzle[1]
            solution_seq = puzzle[2].split(" ")
            if index == 0:
                continue
            if index == positions_num:
                break

            total_puzzles += 1


            print(f"\nposition number {index}")
            board = Board.from_fen(fen)
            board.push(Move.from_uci(solution_seq[0]), add_history=False)
            solution_move = solution_seq[1]

            move, pred_eval = evaluate(board, engine, -10, 10, 10)

            print(f"evaluation prediction: {pred_eval}")
            print(f"solution: {solution_move} | predicted move: {move.uci()}")
            if solution_move == move.uci():
                correct_puzzles += 1
        return correct_puzzles, total_puzzles




def check_if_vertically_flipped_positions_are_equal() -> bool:
    """ checks if flipping the perspective or the nnue of white and black makes difference"""
    engine_mock = init_engine()
    print("White winning | turn white")
    fen = "4k3/8/8/8/8/8/8/4K2R w - - 0 1"
    board = Board.from_fen(fen)
    in_v = engine_mock.build_input(board)
    eval_1 = engine_mock.forward(in_v).item()

    print("White winning | turn black")
    fen = "4k3/8/8/8/8/8/8/4K2R b - - 0 1"
    board = Board.from_fen(fen)
    in_v = engine_mock.build_input(board)
    eval_2 = engine_mock.forward(in_v).item()

    print("Black winning | turn white")
    fen = "4k2r/8/8/8/8/8/8/4K3 w - - 0 1"
    board = Board.from_fen(fen)
    in_v = engine_mock.build_input(board)
    eval_3 = engine_mock.forward(in_v).item()


    print("Black winning | turn black")
    fen = "4k2r/8/8/8/8/8/8/4K3 b - - 0 1"
    board = Board.from_fen(fen)
    in_v = engine_mock.build_input(board)
    eval_4 = engine_mock.forward(in_v).item()

    if eval_1 == eval_2 or eval_3 == eval_4:
        return False
    return True

def eval_fen(fen, eval):
    engine = init_engine()
    board = Board.from_fen(fen)
    target_cp = eval
    target = cp_to_target(target_cp)

    iv = engine.build_input(board)
    pred = engine.forward(iv)
    pred = pred.item()
    print(f"target: {target} | prediction: {pred} | target cp: {target_cp} | prediction cp: {target_to_cp(pred)}")





engine = init_engine()

training_num = 10
epochs = 0
learning_rate = 0.000001

# assess(10)
# for _ in range(10):
#     train(10, learning_rate, TRAINING_DATA_80K_PATH, save_cycle=1000)



while True:
    count, error_av, white_count, white_mae, white_cp_mae, black_count, black_mae, black_cp_mae = train(engine, TRAINING_DATA_80K_PATH, -1, learning_rate)

    with ExitPreventionLock():
        with open("logger.txt", "a") as f:


            print(f"Mean abs error: {error_av}", file=f)
            print(f"Positions count: {count}", file=f)

            print(f"\nNumber of positions with white adv: {white_count}", file=f)
            print(f"White average absolute mae: {white_mae / white_count} | White average absolute cp mae: {white_cp_mae / white_count}", file=f)

            print(f"\nNumber of positions with black adv: {black_count}", file=f)
            print(f"Black average absolute mae: {black_mae / black_count} | Black average absolute cp mae: {black_cp_mae / black_count}", file=f)
            f.write("\n")


    epochs += 1
    print(f"epochs: {epochs}")




