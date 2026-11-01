from .util import *
from .nn import PawnStructCNN

import re
import numpy as np
import numpy.random
import numpy.testing

print()


class Board:
    #TODO: slots later?
    def __init__(self):
        self.pawns = 0
        self.knights = 0
        self.bishops = 0
        self.rooks = 0
        self.queens = 0
        self.kings = 0

        self.king_sq = [0, 0]

        self.occupancy_color = [0, 0]
        self.occupancy = 0

        self.turn = WHITE

        self.castling_rights = 0
        self.ep_square: Square | None = None

        self.half_moves = 0
        self.full_moves = 1

        self.hash = 0

        self.history = []
        self.repetition_table = {}

        # engine related
        self.nnue = [np.zeros((128, 1)), np.zeros((128, 1))]
        self.pawn_nn = np.zeros((8, 1))
        self.debug_feature_indexes = [set(), set()]



    def piece_at(self, square):
        bit = 1 << square
        if bit & self.pawns:
            return PAWN
        if bit & self.knights:
            return KNIGHT
        if bit & self.bishops:
            return BISHOP
        if bit & self.rooks:
            return ROOK
        if bit & self.queens:
            return QUEEN
        if bit & self.kings:
            return KING
        return None


    def color_at(self, square):
        bit = 1 << square
        if bit & self.occupancy_color[WHITE]:
            return WHITE
        elif bit & self.occupancy_color[BLACK]:
            return BLACK
        else:
            return None

    def set_piece_at(self, square, piece_type, color):
        # print(f"\nadd piece ({COLOR_NAME[color]} {PIECE_NAME[piece_type]}) on {SQUARE_NAMES[square]}")
        bit = 1 << square
        if piece_type == PAWN:
            self.pawns |= bit
        elif piece_type == KNIGHT:
            self.knights |= bit
        elif piece_type == BISHOP:
            self.bishops |= bit
        elif piece_type == ROOK:
            self.rooks |= bit
        elif piece_type == QUEEN:
            self.queens |= bit
        elif piece_type == KING:
            self.kings |= bit

        self.occupancy_color[color] |= bit
        self.occupancy |= bit
        self.hash ^= ZobristHasher.get_table_value(color, piece_type, square)

        # if the king moved, the whole accumulator for the king's colour needs to be re-done
        if piece_type == KING:
            # print("THe king goes to a different side")
            self.king_sq[color] = square
            self.nnue[color] = build_accumulator(self, color)
            self.debug_feature_indexes[color] = debug_features_set(self, color)
            # print(f"build feature set for colour {COLOR_NAME[color]}\nNew features:")
            # print(self.debug_feature_indexes[color])
            # for i in self.debug_feature_indexes[color]:
            #     debug_feature_index(i)

            opponent_color = 1 ^ color
            opponent_feature_index = Half_KA_Index(opponent_color == BLACK, KING, False, square, self.king_sq[opponent_color])
            self.nnue[opponent_color] += feature_table[opponent_feature_index]
            # print(f"\nAdded feature to colour {COLOR_NAME[1 ^ color]}")
            # debug_feature_index(opponent_feature_index)
            self.debug_feature_indexes[opponent_color].add(opponent_feature_index)
            # print(f"\ndebug feature set for colour {COLOR_NAME[1 ^ color]}\nFeatures:")
            # print(self.debug_feature_indexes[1 ^ color])
            # for i in self.debug_feature_indexes[1 ^ color]:
            #     debug_feature_index(i)
            return None
        feature_table_white_index = Half_KA_Index(False, piece_type, color == WHITE, square, self.king_sq[WHITE])
        feature_table_black_index = Half_KA_Index(True, piece_type, color == BLACK, square, self.king_sq[BLACK])
        self.nnue[WHITE] += feature_table[feature_table_white_index]
        self.debug_feature_indexes[WHITE].add(feature_table_white_index)

        self.nnue[BLACK] += feature_table[feature_table_black_index]
        self.debug_feature_indexes[BLACK].add(feature_table_black_index)
        # print("adding feature")
        # debug_feature_index(feature_table_white_index)
        # debug_feature_index(feature_table_black_index)
        return None

    def remove_piece_at(self, square):
        # print("------" * 20)
        # self.construct()
        # print(f"\nRemove piece at sq {SQUARE_NAMES[square]}")
        piece_type = self.piece_at(square)
        piece_color = self.color_at(square)
        bit = 1 << square
        if bit & self.pawns:
            self.pawns &= ~bit
        elif bit & self.knights:
            self.knights &= ~bit
        elif bit & self.bishops:
            self.bishops &= ~bit
        elif bit & self.rooks:
            self.rooks &= ~bit
        elif bit & self.queens:
            self.queens &= ~bit
        elif bit & self.kings:
            self.kings &= ~bit
        else:
            return None, None

        self.occupancy_color[piece_color] &= ~bit
        self.occupancy &= ~bit
        self.hash ^= ZobristHasher.get_table_value(piece_color, piece_type, square)

        feature_table_white_index = Half_KA_Index(False, piece_type, piece_color == WHITE, square, self.king_sq[WHITE])
        feature_table_black_index = Half_KA_Index(True, piece_type, piece_color == BLACK, square, self.king_sq[BLACK])

        # print("removing feature")
        # debug_feature_index(feature_table_white_index)
        # debug_feature_index(feature_table_black_index)


        self.nnue[WHITE] -= feature_table[feature_table_white_index]
        self.debug_feature_indexes[WHITE].remove(feature_table_white_index)

        self.nnue[BLACK] -= feature_table[feature_table_black_index]
        self.debug_feature_indexes[BLACK].remove(feature_table_black_index)
        return piece_type, piece_color

    def attacks_mask(self, square: Square):
        bb_square = 1 << square

        if bb_square & self.pawns:
            return BB_PAWN_ATTACKS[self.turn][square]
        elif bb_square & self.knights:
            return BB_KNIGHT_ATTACKS[square]
        elif bb_square & self.kings:
            mask = BB_KING_ATTACKS[square]
            if self.turn == WHITE:
                if self.castling_rights & WHITE_KINGS_CASTLE and ~self.occupancy & 1 << F1:
                    mask |= 1 << G1
                if self.castling_rights & WHITE_QUEENS_CASTLE and ~self.occupancy & 1 << D1:
                    mask |= 1 << C1
            else:
                if self.castling_rights & BLACK_KINGS_CASTLE and ~self.occupancy & 1 << F8:
                    mask |= 1 << G8
                if self.castling_rights & BLACK_QUEENS_CASTLE and ~self.occupancy & 1 << D8:
                    mask |= 1 << C8
            return mask
        else:
            mask = 0
            if bb_square & (self.bishops | self.queens):
                index = (((self.occupancy & BB_DIAGONAL_MASK[square]) * BISHOP_MAGIC[square]) & 0xffff_ffff_ffff_ffff) >> BISHOP_SHIFT[square]
                mask |= BISHOP_ATTACK_TABLE[BISHOP_ATTACK_OFFSET[square] + index]
            if bb_square & (self.rooks | self.queens):
                index = (((self.occupancy & BB_ORTHOGONAL_MASK[square]) * ROOK_MAGIC[square]) & 0xffff_ffff_ffff_ffff) >> ROOK_SHIFT[square]
                mask |= ROOK_ATTACK_TABLE[ROOK_ATTACK_OFFSET[square] + index]


            return mask

    def attackers_mask(self, square: Square, color: Color, occupancy=None):
        occupancy = self.occupancy if occupancy is None else occupancy
        mask = BB_EMPTY
        mask |= BB_PAWN_ATTACKS[1 ^ color][square] & self.pawns
        mask |= BB_KNIGHT_ATTACKS[square] & self.knights
        mask |= BB_KING_ATTACKS[square] & self.kings

        diagonal_index = (((occupancy & BB_DIAGONAL_MASK[square]) * BISHOP_MAGIC[square]) & 0xffff_ffff_ffff_ffff) >> BISHOP_SHIFT[square]
        mask |= BISHOP_ATTACK_TABLE[BISHOP_ATTACK_OFFSET[square] + diagonal_index] & (self.bishops | self.queens)

        orthogonal_index = (((occupancy & BB_ORTHOGONAL_MASK[square]) * ROOK_MAGIC[square]) & 0xffff_ffff_ffff_ffff) >> ROOK_SHIFT[square]
        mask |= ROOK_ATTACK_TABLE[ROOK_ATTACK_OFFSET[square] + orthogonal_index] & (self.rooks | self.queens)

        return mask & self.occupancy_color[color]

    def piece_type_mask(self, piece_type: PieceType):
        if piece_type == PAWN:
            return self.pawns
        elif piece_type == KNIGHT:
            return self.knights
        elif piece_type == BISHOP:
            return self.bishops
        elif piece_type == ROOK:
            return self.rooks
        elif piece_type == QUEEN:
            return self.queens
        elif piece_type == KING:
            return self.kings
        else:
            return 0


    def is_en_passant(self, move):
        return (
            self.ep_square and
            move.to_square == self.ep_square and
            self.piece_at(move.from_square) == PAWN and
            self.piece_at(move.to_square) is None
        )

    def is_capture(self, move):
        return self.piece_at(move.to_square) or self.is_en_passant(move)

    def is_check(self, color=None):
        """ returns if the {color} king is attacked. By default, checks the ally king"""
        color = color if color else self.turn
        king_square = msb_square(self.kings & self.occupancy_color[color])
        return bool(self.attackers_mask(king_square, 1 ^ color))

    def is_move_check(self, move):
        self.push(move)
        res = self.is_check()
        self.pop()
        return res

    def is_move_possible_check(self, move):
        """not as precise as Board.is_move_check, but it is much faster as we don't need to push the move"""
        king_sq = self.king_sq[self.turn ^ 1]
        mask = BB_EMPTY
        mask |= BB_PAWN_ATTACKS[self.turn][king_sq] & self.pawns
        mask |= BB_KNIGHT_ATTACKS[king_sq] & self.knights
        mask |= BB_KING_ATTACKS[king_sq] & self.kings

        diagonal_index = (((self.occupancy & BB_DIAGONAL_MASK[king_sq]) * BISHOP_MAGIC[king_sq]) & 0xffff_ffff_ffff_ffff) >> \
                         BISHOP_SHIFT[king_sq]
        mask |= BISHOP_ATTACK_TABLE[BISHOP_ATTACK_OFFSET[king_sq] + diagonal_index]

        orthogonal_index = (((self.occupancy & BB_ORTHOGONAL_MASK[king_sq]) * ROOK_MAGIC[king_sq]) & 0xffff_ffff_ffff_ffff) >> \
                           ROOK_SHIFT[king_sq]
        mask |= ROOK_ATTACK_TABLE[ROOK_ATTACK_OFFSET[king_sq] + orthogonal_index]
        mask |= BB_KNIGHT_ATTACKS[king_sq]

        return mask & (1 << move.to_square)

    def has_legal_moves(self):
        return next(self.generate_legal_moves(), None) is not None

    def is_insufficient_material(self):
        if (self.knights | self.bishops).bit_count() <= 1 and (self.rooks | self.queens).bit_count() == 0:
            return True
        else:
            return False

    def outcome(self):
        # use outcome enum
        if not self.has_legal_moves():
            if self.is_check():
                return GameResult.CHECKMATE
            else:
                return GameResult.STALEMATE

        elif self.repetition_table.get(self.hash, 0) >= 3:
            return GameResult.DRAW_REPETITION

        elif self.half_moves >= 100:
            return GameResult.DRAW_50_MOVES

        elif self.is_insufficient_material():
            return GameResult.DRAW_INSUFFICIENT_MATERIAL

        return GameResult.ONGOING

    def update_pawn_nn(self):
        print("Update pawn nn")
        print(bitboards_to_plane(self.pawns & self.occupancy_color[self.turn],
                           self.pawns & self.occupancy_color[1 ^ self.turn]))
        self.pawn_nn = PawnStructCNN.forward(bitboards_to_plane(self.pawns & self.occupancy_color[self.turn], self.pawns & self.occupancy_color[1 ^ self.turn]))
        assert np.isfinite(self.pawn_nn).all()


    def push(self, move, *, add_history=True):
        """ assume the move is perfectly legal

        return history: if True, doesnt add to the internal stack, but returns the object
        """

        # print(f"\nPush move: {move.uci()}, turn {COLOR_NAME[self.turn]}")

        if add_history:
            self.history.append(BitBoardState.from_board(self))

        # update en passant
        ep_square = self.ep_square
        if self.ep_square:
            self.hash ^= ZobristHasher.en_passant[self.ep_square % 8]
            self.ep_square = None
        piece, piece_color = self.remove_piece_at(move.from_square)
        captured_piece, captured_piece_color = self.remove_piece_at(move.to_square)

        # handle promotion
        if move.promotion:
            piece = move.promotion

        # handle castling
        if piece == KING and abs(move.to_square - move.from_square) == 2:
            if move.to_square > move.from_square:
                self.remove_piece_at(H1 if self.turn == WHITE else H8)
                self.set_piece_at(F1 if self.turn == WHITE else F8, ROOK, self.turn)
            else:
                self.remove_piece_at(A1 if self.turn == WHITE else A8)
                self.set_piece_at(D1 if self.turn == WHITE else D8, ROOK, self.turn)


        # handle pawn moves
        if piece == PAWN:
            diff = move.to_square - move.from_square

            if diff == 16 and square_rank(move.from_square) == RANK_2:
                self.ep_square = move.from_square + 8
                self.hash ^= ZobristHasher.en_passant[self.ep_square % 8]
            elif diff == -16 and square_rank(move.from_square) == RANK_7:
                self.ep_square = move.from_square - 8
                self.hash ^= ZobristHasher.en_passant[self.ep_square % 8]
            elif move.to_square == ep_square and abs(diff) in (7, 9) and not captured_piece:
                shift = -8 if self.turn == WHITE else 8
                self.remove_piece_at(move.to_square + shift)
                captured_piece = move.to_square + shift


        # update castling rights
        if piece == KING or piece == ROOK:
            self.hash ^= ZobristHasher.castling_rights[self.castling_rights]
            castling_val = CASTLING_RIGHTS_UPDATE_BY_SQUARE.get(move.from_square, 0)
            self.castling_rights &= ~castling_val
            self.hash ^= ZobristHasher.castling_rights[self.castling_rights]

        self.set_piece_at(move.to_square, piece, piece_color)

        # update pawn nn values
        if piece == PAWN or captured_piece == PAWN:
            self.update_pawn_nn()

        # update the move clocks
        if piece == PAWN or captured_piece:
            self.half_moves = 0
        else:
            self.half_moves += 1

        if self.turn == BLACK:
            self.full_moves += 1
        # update the turn
        self.turn ^= 1

        self.hash ^= ZobristHasher.black_turn
        # update repetition table
        if self.repetition_table.get(self.hash):
            self.repetition_table[self.hash] += 1
        else:
            self.repetition_table[self.hash] = 1


        # Zobrist hash assertion check
        try:
            assert self.hash == ZobristHasher.hash(self)
        except AssertionError as err:
            print("Hashing issue")
            print(self.hash)
            print(ZobristHasher.hash(self))
            ZobristHasher.debug(ZobristHasher.hash(self) ^ self.hash)
            self.construct()
            raise err

        # nnue assertion check
        for assert_color in range(2):
            # print(f"After Push Assertion test for colour {COLOR_NAME[assert_color]}", end="")
            try:
                np.testing.assert_almost_equal(self.nnue[assert_color], build_accumulator(self, assert_color), decimal=5)
                # print(" - Passed\n")
            except BaseException:
                print(f"After Push Assertion test for colour {COLOR_NAME[assert_color]}", " - Failed")
                difference = self.debug_feature_indexes[assert_color].symmetric_difference(debug_features_set(self, assert_color))
                print("differences")
                for f in difference:
                    debug_feature_index(f)
                print("sets")
                print(self.debug_feature_indexes[assert_color])
                print(debug_features_set(self, assert_color))

                print("lists diff")
                diff = self.nnue[assert_color] - build_accumulator(self, assert_color)
                print()

                print(f"assert colour: {COLOR_NAME[assert_color]}")
                print(f"error on pushing move {move.uci()}")
                self.construct()
                raise BaseException

    def pop(self):
        if not self.history:
            return False
        prev_state = self.history.pop()
        prev_state.restore(self)

        return prev_state

    def restore(self, state):
        if isinstance(state, BitBoardState):
            state.restore(self)
            return
        else:
            raise NotImplementedError

    def generate_pseudo_legal_moves(self, *, from_mask=BB_ALL, to_mask=BB_ALL) -> (Square, BitBoard):
        non_pawns = self.occupancy_color[self.turn] & ~self.pawns & from_mask
        for from_square in scan_forward_bb(non_pawns):
            moves = self.attacks_mask(from_square) & ~self.occupancy_color[self.turn] & to_mask
            yield from_square, moves

        # generate pawns moves
        ally_pawns = self.pawns & self.occupancy_color[self.turn] & from_mask
        if not ally_pawns:
            return

        # captures
        for from_square in scan_backward_bb(ally_pawns):
            targets = BB_PAWN_ATTACKS[self.turn][from_square] & self.occupancy_color[1 ^ self.turn] & to_mask
            yield from_square, targets

        # advances
        if self.turn == WHITE:
            single_moves = ally_pawns << 8 & ~self.occupancy
            double_moves = single_moves << 8 & ~self.occupancy & BB_RANK_4
        else:
            single_moves = ally_pawns >> 8 & ~self.occupancy
            double_moves = single_moves >> 8 & ~self.occupancy & BB_RANK_5

        for to_square in scan_backward_bb(single_moves & to_mask):
            from_square = to_square + (-8 if self.turn == WHITE else 8)
            yield from_square, 1 << to_square

        for to_square in scan_backward_bb(double_moves & to_mask):
            from_square = to_square + (-16 if self.turn == WHITE else 16)
            yield from_square, 1 << to_square

        # generate en passant
        if not self.ep_square or (1 << self.ep_square) & self.occupancy & to_mask:
            return

        capturers = ally_pawns & BB_PAWN_ATTACKS[1 ^ self.turn][self.ep_square] & (BB_RANK_5 if self.turn == WHITE else BB_RANK_4)
        for from_square in scan_backward_bb(capturers):
            yield from_square, 1 << self.ep_square

        # raise NotImplementedError

    def generate_legal_moves(self, *, from_mask=BB_ALL, to_mask=BB_ALL):
        king_mask = self.kings & self.occupancy_color[self.turn]
        king_square = msb_square(king_mask)

        opposite_color = 1 ^ self.turn
        pinned, pinners, msb_pinned_rays = self.pinned(king_square, self.turn)
        checkers = self.attackers_mask(king_square, opposite_color)
        if checkers:
            evasion_mask = self.generate_evasions_mask(from_mask=from_mask, to_mask=to_mask)
            for to_square in scan_backward_bb(evasion_mask):
                yield Move(king_square, to_square)

            if checkers.bit_count() == 1:
                ray = checkers
                if checkers & (self.rooks | self.bishops | self.queens):
                    ray |= BB_RAYS[king_square][checkers.bit_length()-1]
                for from_square, targets in self.generate_pseudo_legal_moves(from_mask=from_mask, to_mask=to_mask):
                    bb_from_square = 1 << from_square
                    if bb_from_square & pinned or from_square == king_square:
                        continue
                    targets &= ray
                    for to_square in scan_backward_bb(targets):
                        if square_rank(to_square) in (RANK_1, RANK_8) and bb_from_square & self.pawns:
                            yield Move(from_square, to_square, KNIGHT)
                            yield Move(from_square, to_square, BISHOP)
                            yield Move(from_square, to_square, ROOK)
                            yield Move(from_square, to_square, QUEEN)
                        else:
                            yield Move(from_square, to_square)

        else:
            for from_square, targets in self.generate_pseudo_legal_moves(from_mask=from_mask, to_mask=to_mask):
                bb_from_square = 1 << from_square
                if bb_from_square & pinned:
                    targets &= msb_pinned_rays[(pinned >> (from_square + 1)).bit_count()]

                for to_square in scan_backward_bb(targets):
                    if from_square == king_square:
                        if square_distance(from_square, to_square) == 2:
                            for square in scan_forward_bb(BB_RAYS[from_square][to_square]):
                                if self.attackers_mask(square, opposite_color):
                                    break
                            else:
                                yield Move(from_square, to_square)
                            continue

                        elif self.attackers_mask(to_square, opposite_color):
                            continue


                    if square_rank(to_square) in (RANK_1, RANK_8) and bb_from_square & self.pawns:
                        yield Move(from_square, to_square, KNIGHT)
                        yield Move(from_square, to_square, BISHOP)
                        yield Move(from_square, to_square, ROOK)
                        yield Move(from_square, to_square, QUEEN)
                    else:
                        yield Move(from_square, to_square)

    def generate_evasions_mask(self, *, from_mask=BB_ALL, to_mask=BB_ALL):
        king_mask = self.kings & self.occupancy_color[self.turn]
        king_square = msb_square(king_mask)
        opponent_color = 1 ^ self.turn

        attack_mask = BB_KING_ATTACKS[king_square] & from_mask
        mask = 0
        for to_square in scan_forward_bb(attack_mask):
            mask |= 1 << to_square if not self.attackers_mask(to_square, opponent_color, self.occupancy & ~king_mask) else 0

        return mask & ~self.occupancy_color[self.turn] & to_mask

    def pinned(self, king_sq: Square, color: Color) -> (BitBoard, list[Square]):
        """ the pinner squares are done using the msb approach, thus each pinner_square is the current msb"""
        opponent_color = 1 ^ color
        possible_pinners = 0

        diagonal_index = (((self.occupancy_color[opponent_color] & BB_DIAGONAL_MASK[king_sq]) * BISHOP_MAGIC[king_sq]) & 0xffff_ffff_ffff_ffff) >> BISHOP_SHIFT[king_sq]
        possible_pinners |= BISHOP_ATTACK_TABLE[BISHOP_ATTACK_OFFSET[king_sq] + diagonal_index] & (self.bishops | self.queens)

        orthogonal_index = (((self.occupancy_color[opponent_color] & BB_ORTHOGONAL_MASK[king_sq]) * ROOK_MAGIC[king_sq]) & 0xffff_ffff_ffff_ffff) >> ROOK_SHIFT[king_sq]
        possible_pinners |= ROOK_ATTACK_TABLE[ROOK_ATTACK_OFFSET[king_sq] + orthogonal_index] & (self.rooks | self.queens)

        possible_pinners &= self.occupancy_color[opponent_color]
        # attackers mask? possibly
        pinned = BB_EMPTY
        pinners = BB_EMPTY
        pinned_ray = []
        for square in scan_forward_bb(possible_pinners):
            potential_blockers = BB_BETWEEN[king_sq][square] & self.occupancy
            if potential_blockers.bit_count() == 1:
                pinned |= potential_blockers & self.occupancy_color[color]
                pinned_ray.append(BB_BETWEEN[king_sq][square] | 1 << square)
                pinners |= 1 << square

        return pinned, pinners, pinned_ray


    def san_without_suffix(self, move):
        if move.to_square == self.ep_square:
            return f"{FILE_NAMES[square_file(move.from_square)]}x{SQUARE_NAMES[self.ep_square]}"

        piece = self.piece_at(move.from_square)
        if piece == KING and abs(move.from_square - move.to_square) == 2:
            if move.from_square > move.to_square:
                return "O-O-O"
            else:
                return "O-O"

        piece_sym = PIECE_SYM[piece]
        san = piece_sym.upper() if piece != PAWN else ""
        capture = bool(self.piece_at(move.to_square))

        if piece == PAWN:
            if capture:
                san += FILE_NAMES[square_file(move.from_square)] + "x"
            san += SQUARE_NAMES[move.to_square]
            if move.promotion:
                san += "=" + PIECE_SYM[move.promotion].upper()
            return san

        competition = self.attackers_mask(move.to_square, self.turn) & ~(1 << move.from_square) & self.piece_type_mask(piece)

        if competition:
            file, rank = "", ""
            for sq in scan_forward_bb(competition):
                if square_rank(sq) == square_rank(move.from_square):
                    file = FILE_NAMES[square_file(move.from_square)]
                if square_file(sq) == square_file(move.from_square):
                    rank = RANK_NAMES[square_rank(move.from_square)]

            if file == rank == "":
                file = FILE_NAMES[square_file(move.from_square)]

            san += file + rank

        san += SQUARE_NAMES[move.to_square]
        return san


    def san(self, move):
        """assume move is legal"""
        san = self.san_without_suffix(move)
        self.push(move)
        # might need to consider raw push
        if self.outcome() == GameResult.CHECKMATE:
            san += "#"
        elif self.is_check():
            san += "+"
        self.pop()

        return san

    def parse_san(self, san):
        if san in ["O-O", "O-O+", "O-O#", "0-0", "0-0+", "0-0#"]:
            if self.turn == WHITE and self.castling_rights & WHITE_KINGS_CASTLE:
                return Move(E1, G1)
            elif self.turn == BLACK and self.castling_rights & BLACK_KINGS_CASTLE:
                return Move(E8, G1)
        elif san in ["O-O-O", "O-O-O+", "O-O-O#", "0-0-0", "0-0-0+", "0-0-0#"]:
            if self.turn == WHITE and self.castling_rights & WHITE_QUEENS_CASTLE:
                return Move(E1, C1)
            elif self.turn == BLACK and self.castling_rights & BLACK_QUEENS_CASTLE:
                return Move(E8, C8)

        match = SAN_REGEX.match(san)
        # piece sym, file, rank, to square, promotion
        if not match:
            raise UnrecognisedSanMove(san)

        sym = match.group(1)
        piece_type = PIECE_TYPES[PIECE_SYM.index(sym.lower()) - 1] if sym else PAWN
        to_square = SQUARES[SQUARE_NAMES.index(match.group(4))]

        p = match.group(5)
        promotion = PIECE_TYPES[PIECE_SYM.index(p) - 1] if p else 0

        competition = self.piece_type_mask(piece_type)
        file = match.group(2)
        rank = match.group(3)
        if rank:
            competition &= BB_RANKS[RANK_NAMES.index(rank)]
        if file:
            competition &= BB_FILES[FILE_NAMES.index(file)]

        if not competition:
            raise UnrecognisedSanMove(san)

        for move_candidate in self.generate_legal_moves(from_mask=competition, to_mask=1 << to_square):
            if self.piece_at(move_candidate.from_square) == piece_type and move_candidate.promotion == promotion:
                return move_candidate
        else:
            raise UnrecognisedSanMove(san)


    def copy_from(self, board):
        if not isinstance(board, Board):
            raise TypeError(f"The object to copy from should be of type {Board}")

        self.pawns = board.pawns
        self.knights = board.knights
        self.bishops = board.bishops
        self.rooks = board.rooks
        self.queens = board.queens
        self.kings = board.kings

        self.occupancy_color = board.occupancy_color[:]
        self.castling_rights = board.castling_rights
        self.ep_square = board.ep_square
        self.half_moves = board.half_moves
        self.full_moves = board.full_moves
        self.hash = board.hash

        self.occupancy = board.occupancy
        self.turn = board.turn

        self.repetition_table = board.repetition_table.copy()

        self.king_sq = board.king_sq
        np.copyto(self.nnue[0], board.nnue[0])
        np.copyto(self.nnue[1], board.nnue[1])
        np.copyto(self.pawn_nn, board.pawn_nn)

        self.history = board.history.copy()

        self.debug_feature_indexes[0] = board.debug_feature_indexes[0].copy()
        self.debug_feature_indexes[1] = board.debug_feature_indexes[1].copy()


    @classmethod
    def from_fen(cls, fen: str):
        bit_board = cls()

        sections = fen.split(" ")

        for file_i, row in enumerate(sections[0].split("/")):
            empty = 0
            for piece in row:
                if piece.isnumeric():
                    empty += int(piece)
                else:
                    square = (7 - file_i) * 8 + empty
                    piece_colour = WHITE if piece.isupper() else BLACK
                    piece_type = PIECE_SYM.index(piece.lower())
                    bit_board.set_piece_at(square, piece_type, piece_colour)
                    empty += 1

        if sections[1] == "w":
            bit_board.turn = WHITE
        if sections[1] == "b":
            bit_board.turn = BLACK

        castles = sections[2]
        if "K" in castles:
            bit_board.castling_rights |= WHITE_KINGS_CASTLE
        if "Q" in castles:
            bit_board.castling_rights |= WHITE_QUEENS_CASTLE
        if "k" in castles:
            bit_board.castling_rights |= BLACK_KINGS_CASTLE
        if "q" in castles:
            bit_board.castling_rights |= BLACK_QUEENS_CASTLE

        bit_board.ep_square = SQUARE_NAMES.index(sections[3]) if sections[3] != "-" else None

        bit_board.half_moves = int(sections[4])
        bit_board.full_moves = int(sections[5])

        bit_board.hash = ZobristHasher.hash(bit_board)

        # print("\nthis is the debug")
        bit_board.nnue = [build_accumulator(bit_board, WHITE), build_accumulator(bit_board, BLACK)]
        # bit_board.debug_feature_indexes = [debug_features_set(bit_board, WHITE), debug_features_set(bit_board, BLACK)]
        #
        # try:
        #     np.testing.assert_allclose(bit_board.nnue, [build_accumulator(bit_board, WHITE), build_accumulator(bit_board, BLACK)], rtol=1e-5, atol=1e-5)
        # except BaseException as err:
        #     print("sets")
        #     print(bit_board.debug_feature_indexes[WHITE].symmetric_difference(debug_features_set(bit_board, WHITE)))
        #     print(bit_board.debug_feature_indexes[BLACK].symmetric_difference(debug_features_set(bit_board, BLACK)))
        #     print(bit_board.nnue)
        #     raise err
        # print(bit_board.debug_feature_indexes)

        # print("---" * 12, "Finished init from fen", "---" * 12)
        # print("White features")
        # for i in bit_board.debug_feature_indexes[0]:
        #     debug_feature_index(i)
        # print("BLACK features")
        # for i in bit_board.debug_feature_indexes[1]:
        #     debug_feature_index(i)
        # print()
        bit_board.update_pawn_nn()
        return bit_board


    def to_fen(self) -> str:
        fen = ""

        # --DEBUG--
        # print("\nFEN INPUT")
        # print(board.player)
        # print(board.kings_castle)
        # print(board.possible_en_passant)
        # print(board.half_moves, board.full_moves)
        # print()

        # Positions (section 1)
        for rank in range(7, -1, -1):
            empty = 0

            for file in range(8):
                square = rank * 8 + file
                piece, color = self.piece_at(square), self.color_at(square)

                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                    sym = PIECE_SYM[piece]
                    fen += sym.upper() if color == WHITE else sym.lower()
                    empty = 0

            if empty > 0:
                fen += str(empty)

            if rank != 0:
                fen += "/"

        if self.turn == WHITE:
            fen += " w"
        else:
            fen += " b"

        # Castling (sections 2 and 3)
        possible_castles = ""
        if self.castling_rights & WHITE_KINGS_CASTLE:
            possible_castles += "K"
        if self.castling_rights & WHITE_QUEENS_CASTLE:
            possible_castles += "Q"
        if self.castling_rights & BLACK_KINGS_CASTLE:
            possible_castles += "k"
        if self.castling_rights & BLACK_QUEENS_CASTLE:
            possible_castles += "q"

        fen += f" {possible_castles if possible_castles else '-'}"

        # en passant
        if self.ep_square is None:
            fen += " -"
        else:
            fen += f" {SQUARE_NAMES[self.ep_square]}"

        # half moves and full moves
        fen += f" {self.half_moves} {self.full_moves}"


        return fen

    def construct(self):
        # A function that prints the board. NOTHING TO BE CHANGED HERE
        print(f"{'           ' * 2}Black")
        print("|-----" * 8 + "|")
        for rank in range(7, -1, -1):
            for file in range(8):
                square = rank * 8 + file
                piece, color = self.piece_at(square), self.color_at(square)

                if piece is None:
                    val = " "
                else:
                    sym = PIECE_SYM[piece]
                    val = sym.upper() if color == WHITE else sym.lower()
                print(f"|  {val}  " if len(str(val)) == 1 else f"|  {val} ", end="")
            print("|", end="")
            print(f"  {rank+1}")
            print("|-----" * 8 + "|")
        # section to add letters
        print("   ", end="")
        # h - 104, a - 97
        for letter in range(97, 105):  # H -> A ~ (104, 96, -1)
            print(f"{chr(letter)}     ", end="")
        print(f"\n{'           ' * 2}White")
        print(f"\nFEN: {self.to_fen()}")

