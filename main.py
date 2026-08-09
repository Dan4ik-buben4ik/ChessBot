from Chess_lib import *
from Chess_lib import MoveGenerator
from Engine.engine import Engine, logger

# only queens and kings: "3qk3/8/8/8/8/8/8/3QK3 w - - 0 1"
# only rooks and kings: r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1
# only bishops and kings: 2b1kb2/8/8/8/8/8/8/2B1KB2 w - - 0 1
# only knights and kings:1n2k1n1/8/8/8/8/8/8/1N2K1N1 w - - 0 1
# en_passant check: "4k3/8/8/8/1p6/8/P7/4K3 w - - 0 1"
# discovered-check check: 4k3/8/8/8/8/5p2/4P3/K3R3 w - - 0 1
# double check: "8/8/8/8/4k3/5p2/4P3/K3R3 w - - 0 1"
# all pawns on the last row: "2R5/PPPPPPPP/8/8/8/8/8/k6K w - - 0 1"
# starting position: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


board = Board(fen="4k3/8/8/8/1p6/8/P7/4K3 w - - 0 1")
board.construct()
enigne = Engine(board, -100, 100, 30)  # depth 10 fails
# print("Possible moves")
# possible_moves = list(MoveGenerator.generate_legal_moves(board))
# print(possible_moves)
# print(enigne.evaluate())
# print(enigne.generate())
# a2a3, e8d8, a3a4, d8c8, a4a5, c8b8, a5a6, b8a7, e1d1, a7a6
# error path: root/a2a3/e8d8/a3a4/d8c8/a4a5/c8b8/a5a6/b4b3/a7b8q

print("Possible moves")
possible_moves = list(MoveGenerator.generate_legal_moves(board))
print(possible_moves)
evaluation = enigne.evaluate()
print(evaluation)
#TODO: yields and error when depth >=9
print(enigne.generate())
print(evaluation)
# logger.print_dict()
while True:
    # print("Possible moves")
    # possible_moves = list(MoveGenerator.generate_legal_moves(board))
    # print(possible_moves)
    # evaluation = enigne.evaluate()
    # print(evaluation)
    # #TODO: yields and error when depth >=9
    # print(enigne.generate())
    # print(evaluation)
    # logger.print_dict()
    logger.view_dict()


    # input_move = input("Move Input (uci): ")
    # if input_move == "pop":
    #     board.pop()
    #     board.construct()
    #     continue
    # elif input_move == "print":
    #     logger.print_dict()
    #     continue
    # elif input_move == "view":
    #     logger.view_dict()
    #     continue
    # move = Move.from_uci(input_move)
    #
    # if move in possible_moves:
    #     board.push(move)
    #     board.construct()
    #     # board.pop()
    #     # board.construct()
#
#
#
#         # end, winner = board.game_end_check(MoveGenerator)
#         # if end:
#         #     print(f"winner: {winner}")
#         #     break



