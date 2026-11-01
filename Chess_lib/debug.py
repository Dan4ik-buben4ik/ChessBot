from .util import *


import numpy as np
import numpy.testing


def debug(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        print(res)
        return res
    return wrapper

def assert_nnue_equal_to_current_position_accumulators(board, output_header):
    for assert_color in range(2):
        try:
            print(f"{output_header}for colour {COLOR_NAME[assert_color]}", end="")
            np.testing.assert_almost_equal(board.nnue[assert_color], build_accumulator(board, assert_color), decimal=5)
            print(" - Passed")
        except BaseException as err:
            print(" - Failed")
            print("ERROR HAD OCCURED\n")
            # print("difference")
            # difference = bit_board.debug_feature_indexes[0].symmetric_difference(
            #     debug_features_set(bit_board, 0))
            print("bitboard features")
            for f in board.debug_feature_indexes[assert_color]:
                debug_feature_index(f)

            print("\ndesired bitboard features")
            for f in debug_features_set(board, assert_color):
                debug_feature_index(f)



            print("\nsets")
            print(board.debug_feature_indexes[assert_color])
            print(debug_features_set(board, assert_color))

            raise err
# d8c7/a1b1

def debug_feature_data(bit_board, uci_move):
    move = Move.from_uci(uci_move)

    print("---" * 12)
    print("start debug testing")
    ally_color = bit_board.color_at(move.from_square)
    piece_type = bit_board.piece_at(move.from_square)

    king_sq = bit_board.king_sq[BLACK]
    print("starting data")
    print(
        f"piece type: {PIECE_NAME[piece_type]} | piece square: {SQUARE_NAMES[move.from_square]} | ally: 0 | king sq: {SQUARE_NAMES[king_sq]}")
    HalfKAIndex = Half_KA_Index(True, piece_type, False, move.from_square, king_sq)
    print("\nIndex data")
    debug_feature_index(HalfKAIndex)