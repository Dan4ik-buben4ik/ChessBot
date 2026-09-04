from util import *
from util import _subsets, _sliding_attacks

import random
import array
import os


def find_magic_numbers(square: Square, mask: BitBoard, deltas):
    """generates the magic numbers to find the index of attacking ray per a blockers configuration"""
    rng = random.Random()
    shift = 64 - mask.bit_count()


    occupancies = []
    attacks = []

    for blockers in _subsets(mask):
        occupancies.append(blockers)
        attacks.append(_sliding_attacks(square, blockers, deltas))

    tried = set()
    attempt = 0
    while True:
        attempt += 1
        # if attempt % 100_000 == 0:
        #     print(attempt)
        magic = rng.getrandbits(64) & rng.getrandbits(64) & rng.getrandbits(64)
        if magic in tried:
            continue
        tried.add(magic)
        table = [0 for _ in range(1 << (64-shift))]

        failed = False

        for blockers, attack in zip(occupancies, attacks):
            index = ((blockers * magic) & 0xffff_ffff_ffff_ffff) >> shift

            if table[index] != 0:
                if table[index] != attack:
                    failed = True
                    break
            else:
                table[index] = attack

        if not failed:
            return magic, shift, table






print("rook")
ROOK_ATTACKS = []  # Square, index : BitBoard
ROOK_MAGIC = []  # Square: magic number
ROOK_SHIFT = []  # Square: shift value
for square in SQUARES:
    number, shift, attacks = find_magic_numbers(square, BB_ORTHOGONAL_MASK[square], [8, 1, -1, -8])
    # print(number, shift)

    ROOK_MAGIC.append(number)
    ROOK_SHIFT.append(shift)
    ROOK_ATTACKS.append(attacks)




print("bishop")
BISHOP_ATTACKS = []  # Square, index : BitBoard
BISHOP_MAGIC = []  # Square: magic number
BISHOP_SHIFT = []  # Square: shift value
for square in SQUARES:
    number, shift, attacks = find_magic_numbers(square, BB_DIAGONAL_MASK[square], [7, 9, -7, -9])
    # print(number, shift)

    BISHOP_MAGIC.append(number)
    BISHOP_SHIFT.append(shift)

    BISHOP_ATTACKS.append(attacks)


# with open("magic_table.bin", "wb") as file:
#     print("saving rook values")
#     for magic in ROOK_MAGIC:
#         file.write(struct.pack("<Q", magic))
#     for shift in ROOK_SHIFT:
#         file.write(struct.pack("<Q", shift))
#     for square_table in ROOK_ATTACKS:
#         for mask in square_table:
#             file.write(struct.pack("<Q", mask))
#
#     print("saving bishop values")
#     for magic in BISHOP_MAGIC:
#         file.write(struct.pack("<Q", magic))
#     for shift in BISHOP_SHIFT:
#         file.write(struct.pack("<Q", shift))
#     for square_table in BISHOP_ATTACKS:
#         for mask in square_table:
#             file.write(struct.pack("<Q", mask))
#
#     file.flush()


# print("ROOK tables:")
# print(f"len ROOK_ATTACKS = {len(ROOK_ATTACKS)}")
# for sq, row in enumerate(ROOK_ATTACKS):
#     print(f"\nsquare: {SQUARE_NAMES[sq]}")
#     expected = 1 << (64 - ROOK_SHIFT[sq])
#     print(
#         "shift =", ROOK_SHIFT[sq],
#         "actual =", len(row),
#         "expected =", expected
#     )
#     print(len(ROOK_ATTACKS[sq]) == 1 << (64 - ROOK_SHIFT[sq]))
#
# print("BISHOP tables:")
# for sq, row in enumerate(BISHOP_ATTACKS):
#     print(f"\nsquare: {SQUARE_NAMES[sq]}")
#     expected = 1 << (64 - BISHOP_SHIFT[sq])
#     print(
#         "shift =", BISHOP_SHIFT[sq],
#         "actual =", len(row),
#         "expected =", expected
#     )
#     print(len(BISHOP_ATTACKS[sq]) == 1 << (64 - BISHOP_SHIFT[sq]))


if os.path.exists("magic_table.bin"):
    os.remove("magic_table.bin")

with open("magic_table.bin", "wb") as file:
    array.array("Q", ROOK_MAGIC).tofile(file)
    array.array("B", ROOK_SHIFT).tofile(file)

    flatten = array.array("Q", (item for row in ROOK_ATTACKS for item in row))
    flatten.tofile(file)

    array.array("Q", BISHOP_MAGIC).tofile(file)
    array.array("B", BISHOP_SHIFT).tofile(file)

    flatten = array.array("Q", (item for row in BISHOP_ATTACKS for item in row))
    flatten.tofile(file)

    file.flush()


print(
    "size:",
    os.path.getsize("magic_table.bin") / 1024**2,
    "MiB"
)


# check the reading method
with open("magic_table.bin", "rb") as file:
    qROOK_MAGIC = array.array("Q")
    qROOK_MAGIC.fromfile(file, 64)

    qROOK_SHIFT = array.array("B")
    qROOK_SHIFT.fromfile(file, 64)

    qROOK_ATTACK_OFFSET = array.array("Q")
    qROOK_ATTACK_TABLE = array.array("Q")

    offset = 0
    for sq, shift in enumerate(ROOK_SHIFT):
        size = 1 << (64 - shift)
        qROOK_ATTACK_OFFSET.append(offset)

        attack = array.array("Q")
        attack.fromfile(file, size)

        assert len(attack) == size

        qROOK_ATTACK_TABLE.extend(attack)

        offset += size

    qBISHOP_MAGIC = array.array("Q")
    qBISHOP_MAGIC.fromfile(file, 64)

    qBISHOP_SHIFT = array.array("B")
    qBISHOP_SHIFT.fromfile(file, 64)

    qBISHOP_ATTACK_OFFSET = array.array("Q")
    qBISHOP_ATTACK_TABLE = array.array("Q")

    offset = 0
    for sq, shift in enumerate(BISHOP_SHIFT):
        size = 1 << (64 - shift)
        qBISHOP_ATTACK_OFFSET.append(offset)

        attack = array.array("Q")
        attack.fromfile(file, size)

        assert len(attack) == size

        qBISHOP_ATTACK_TABLE.extend(attack)

        offset += size


print("checking the decoding")

for sq in range(64):
    size = 1 << (64 - ROOK_SHIFT[sq])
    offset = qROOK_ATTACK_OFFSET[sq]

    for index in range(size):
        assert (
            qROOK_ATTACK_TABLE[offset + index]
            == ROOK_ATTACKS[sq][index]
        )

print("passed rook checks")

for sq in range(64):
    size = 1 << (64 - BISHOP_SHIFT[sq])
    offset = qBISHOP_ATTACK_OFFSET[sq]

    for index in range(size):
        assert (
            qBISHOP_ATTACK_TABLE[offset + index]
            == BISHOP_ATTACKS[sq][index]
        )

print("passed bishop checks")