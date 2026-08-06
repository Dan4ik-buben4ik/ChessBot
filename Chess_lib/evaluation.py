from util import TurnColor, EvalTable
from pieces import Pawn
import MoveGenerator as MoveGen



class StaticEvaluation:
    @classmethod
    def evaluate(cls, board):
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
    def _material(board):
        score = 0
        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue
                if piece.name == "King":
                    continue
                change = EvalTable.piece_value[piece.name]
                if piece.color == TurnColor.WHITE:
                    score += change
                else:
                    score -= change
        return score

    @staticmethod
    #TODO: actually add values to the table
    def _piece_square(board) -> int:
        score = 0
        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue
                elif piece.name == "Pawn" or piece.name == "King":
                    continue

                change = EvalTable.activity[piece.pos[1]][piece.pos[0]] * EvalTable.activity_scale * EvalTable.piece_value[piece.name]
                if piece.color == TurnColor.WHITE:
                    score += change
                else:
                    score -= change
        return score

    @staticmethod
    def _mobility(board) -> int:
        current_moves = len(list(MoveGen.generate_legal_moves(board)))
        board.switch_turn()
        opponent_moves = len(list(MoveGen.generate_legal_moves(board)))
        board.switch_turn()
        score = (current_moves - opponent_moves) * EvalTable.mobility + EvalTable.tempo
        if board.turn == TurnColor.BLACK:
            score *= -1


        return score

    @staticmethod
    def _pawn_structure(board) -> int:
        score = 0
        for row in board.board:
            for piece in row:
                if piece == 0:
                    continue
                elif piece.name != "Pawn":
                    continue

                #TODO: make the passed pawn work differently
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
    def _king_safety(board) -> int:
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
    def _rook_activity(board) -> int:
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
    def _bishop_pair(board) -> int:
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

