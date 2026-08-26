from Chess_lib import *
from Chess_lib.util import *
from Chess_lib.util import _subsets, _sliding_attacks

# only queens and kings: "3qk3/8/8/8/8/8/8/3QK3 w - - 0 1"
# only rooks and kings: r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1  hash = 8443997070231762362
# only bishops and kings: 2b1kb2/8/8/8/8/8/8/2B1KB2 w - - 0 1
# only knights and kings:1n2k1n1/8/8/8/8/8/8/1N2K1N1 w - - 0 1
# en_passant check: "4k3/8/8/8/1p6/8/P7/4K3 w - - 0 1"
# discovered-check check: 4k3/8/8/8/8/5p2/4P3/K3R3 w - - 0 1
# double check: "8/8/8/8/4k3/5p2/4P3/K3R3 w - - 0 1"
# all pawns on the last row: "2R5/PPPPPPPP/8/8/8/8/8/k6K w - - 0 1"
# starting position: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# bit_board = Board.from_fen("4k3/8/8/8/1p6/8/P7/4K3 w - - 0 1")
# bit_board.construct()
#
# move = Move.from_uci("a2a4")
# bit_board.push(move)
# bit_board.construct()


with open("save.txt", "a") as save:
    save.write("\nROOK\n")
    save.flush()


print("rook")
ROOK_ATTACKS = []  # Square, index : BitBoard
ROOK_MAGIC = []  # Square: magic number
ROOK_SHIFT = []  # Square: shift value
for square in SQUARES:
    with open("save.txt", "a") as save:
        number, shift = find_magic_numbers(square, BB_ORTHOGONAL_MASK[square], [8, 1, -1, -8])
        save.write(f"\n{SQUARE_NAMES[square]} | {number} | {shift}\n")
        print(number, shift)

        ROOK_MAGIC.append(number)
        ROOK_SHIFT.append(shift)

        attacks = {}
        for blockers in _subsets(BB_ORTHOGONAL_RAYS[square]):
            index = ((blockers * number) & 0xffff_ffff_ffff_ffff) >> shift

            attacks[index] = _sliding_attacks(square, blockers, [8, 1, -1, -8])
            ROOK_ATTACKS.append(attacks)

        save.flush()


with open("save.txt", "a") as save:
    save.write("\nBISHOP\n")
    save.flush()

print("bishop")
BISHOP_ATTACKS = []  # Square, index : BitBoard
BISHOP_MAGIC = []  # Square: magic number
BISHOP_SHIFT = []  # Square: shift value
for square in SQUARES:
    with open("save.txt", "a") as save:
        number, shift = find_magic_numbers(square, BB_DIAGONAL_MASK[square], [7, 9, -7, -9])
        save.write(f"\n{SQUARE_NAMES[square]} | {number} | {shift}\n")
        print(number, shift)

        BISHOP_MAGIC.append(number)
        BISHOP_SHIFT.append(shift)

        attacks = {}
        for blockers in _subsets(BB_ORTHOGONAL_RAYS[square]):
            index = ((blockers * number) & 0xffff_ffff_ffff_ffff) >> shift

            attacks[index] = _sliding_attacks(square, blockers, [7, 9, -7, -9])
            BISHOP_ATTACKS.append(attacks)


import json
with open("save.json", "a") as save:
    json.dump({"ROOK": 0}, save, indent=4)
    json.dump(ROOK_ATTACKS, save, indent=4)
    json.dump(ROOK_MAGIC, save, indent=4)
    json.dump(ROOK_SHIFT, save, indent=4)

    json.dump({"BISHOP": 1}, save, indent=4)
    json.dump(BISHOP_ATTACKS, save, indent=4)
    json.dump(BISHOP_MAGIC, save, indent=4)
    json.dump(BISHOP_SHIFT, save, indent=4)
    save.flush()

# ROOK_ATTACKS = []  # Square, index : BitBoard
# ROOK_MAGIC = []  # Square: magic number
# ROOK_SHIFT = []  # Square: shift value
#
# square = H8
# number, shift = find_magic_numbers(square, BB_ORTHOGONAL_MASK[square], [8, 1, -1, -8])
# print(number, shift)
#
# ROOK_MAGIC.append(number)
# ROOK_SHIFT.append(shift)
#
# attacks = {}
# for blockers in _subsets(BB_ORTHOGONAL_RAYS[square]):
#     index = ((blockers * number) & 0xffff_ffff_ffff_ffff) >> shift
#
#     attacks[index] = _sliding_attacks(square, blockers, [8, 1, -1, -8])
#     print()
#     print(blockers)
#     print(attacks[index])
#
# ROOK_ATTACKS.append(attacks)
