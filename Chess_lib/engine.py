import dataclasses
from .util import *
from .loader import Board




@dataclasses.dataclass(frozen=True)
class EvalTable:
    #all in centipawns
    PAWN = 100
    KNIGHT = 300
    BISHOP = 300
    ROOK = 500
    QUEEN = 900

    CENTRE =  20
    EXTENDED_CENTRE = 10
    EDGE = -10


    bishop_pair = 30
    doubled_pawn = - 15
    isolated_pawn = -20
    passed_pawn = 45
    mobility = 3
    activity_scale = 0.02
    king_open_file = -50
    rook_open_file = 20
    tempo = 10


class StaticEvaluation:
    @classmethod
    def evaluate(cls, board: Board):
        score = 0
        score += cls._material(board)
        score += cls._piece_square(board)
        score += cls._mobility(board)
        score += cls._pawn_structure(board)
        score += cls._king_safety(board)
        score += cls._rook_activity(board)
        score += cls._bishop_pair(board)
        return score

    @staticmethod
    def _material(board: Board):
        white = (
            (board.knights & board.occupancy[WHITE]).bit_count() * EvalTable.KNIGHT +
            (board.bishops & board.occupancy[WHITE]).bit_count() * EvalTable.BISHOP +
            (board.rooks & board.occupancy[WHITE]).bit_count() * EvalTable.ROOK +
            (board.queens & board.occupancy[WHITE]).bit_count() * EvalTable.QUEEN +
            (board.pawns & board.occupancy[WHITE]).bit_count() * EvalTable.PAWN
        )
        black = (
            (board.knights & board.occupancy[BLACK]).bit_count() * EvalTable.KNIGHT +
            (board.bishops & board.occupancy[BLACK]).bit_count() * EvalTable.BISHOP +
            (board.rooks & board.occupancy[BLACK]).bit_count() * EvalTable.ROOK +
            (board.queens & board.occupancy[BLACK]).bit_count() * EvalTable.QUEEN +
            (board.pawns & board.occupancy[BLACK]).bit_count() * EvalTable.PAWN
        )
        return white - black


    @staticmethod
    def _piece_square(board: Board) -> int:
        white = (
            (board.occupancy_color[WHITE] & BB_CENTRE).bit_count() * EvalTable.CENTRE +
            (board.occupancy_color[WHITE] & BB_EXTENDED_CENTRE).bit_count() * EvalTable.EXTENDED_CENTRE +
            (board.occupancy_color[WHITE] & BB_EDGES).bit_count() * EvalTable.EDGE
        )
        black = (
            (board.occupancy_color[BLACK] & BB_CENTRE).bit_count() * EvalTable.CENTRE +
            (board.occupancy_color[BLACK] & BB_EXTENDED_CENTRE).bit_count() * EvalTable.EXTENDED_CENTRE +
            (board.occupancy_color[BLACK] & BB_EDGES).bit_count() * EvalTable.EDGE
        )
        return white - black

    @staticmethod
    def _mobility(board: Board) -> int:
        current_moves = len(list(board.generate_pseudo_legal_moves()))
        board.turn ^= 1
        opponent_moves = len(list(board.generate_pseudo_legal_moves()))
        board.turn ^= 1
        score = (current_moves - opponent_moves) * EvalTable.mobility + EvalTable.tempo
        if board.turn == BLACK:
            score *= -1

        return score

    @staticmethod
    def _pawn_structure(board: Board) -> int:
        score = 0
        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue
                elif piece.name != "Pawn":
                    continue

                #TODO: make the passed pawn work differently, aka the further it is the better and check if there are any pawns in front
                if piece.color == TurnColor.WHITE and piece.pos[1] <= 2 and not isinstance(board.board[piece.pos[1] - 1][piece.pos[0]], Pawn):
                    score += EvalTable.passed_pawn

                if piece.color == TurnColor.BLACK and piece.pos[1] >= 6 and not isinstance(board.board[piece.pos[1] + 1][piece.pos[0]], Pawn):
                    score += EvalTable.passed_pawn

                change = 0
                isolated = True
                doubled = False

                for x_i in (-1, 0, 1):
                    for y_i in (-1, 0, 1):
                        if x_i == y_i == 0:
                            continue
                        try:
                            close_pawn = board.board[piece.pos[1] + y_i][piece.pos[0] + x_i]
                            if close_pawn == 0:
                                continue

                            isolated = False
                            if x_i == 0:
                                doubled = True
                        except IndexError:
                            continue

                change += EvalTable.isolated_pawn if isolated else 0
                change += 1/2 * EvalTable.doubled_pawn if doubled else 0

                if piece.color == TurnColor.WHITE:
                    score += change
                else:
                    score -= change

        return score

    @staticmethod
    def _king_safety(board: Board) -> int:
        """
        include open files near the king and the detection of endgame/middle game

        """
        score = 0
        white_king = board.kings[TurnColor.WHITE]
        black_king = board.kings[TurnColor.BLACK]

        if board.is_endgame:
            score += EvalTable.activity[white_king.pos[1]][white_king.pos[0]] * EvalTable.activity_scale
            score -= EvalTable.activity[black_king.pos[1]][black_king.pos[0]] * EvalTable.activity_scale
        else:
            # checks the open files around the kings
            open_files = board.open_files
            for i in (-1, 0, 1):
                try:
                    file = open_files[white_king.pos[0] + i]
                    if file:
                        score += EvalTable.king_open_file
                except IndexError:
                    continue

                try:
                    file = open_files[black_king.pos[0] + i]
                    if file:
                        score -= EvalTable.king_open_file
                except IndexError:
                    continue


        return score

    @staticmethod
    def _rook_activity(board: Board) -> int:
        open_files = board.open_files

        score = 0
        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue
                elif piece.name != "Rook":
                    continue

                if open_files[piece.pos[0]]:

                    if piece.color == TurnColor.WHITE:
                        score += EvalTable.rook_open_file
                    else:
                        score -= EvalTable.rook_open_file
        return score

    @staticmethod
    def _bishop_pair(board: Board) -> int:
        score = 0
        pair_white = 0
        pair_black = 0

        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue
                if piece.name == "Bishop":
                    if piece.color == TurnColor.WHITE:
                        pair_white += 1
                    else:
                        pair_black += 1

        if pair_white >= 2:
            score += EvalTable.bishop_pair

        if pair_black >= 2:
            score -= EvalTable.bishop_pair

        return score