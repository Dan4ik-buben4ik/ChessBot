from types import GeneratorType
from loader import Board

class MoveGenerator:
    def __init__(self, board: Board):
        self.board = board

    def get_all_possible_moves(self, turn_color):
        is_check, king_attackers_pos = self.board.check_if_king_attacked(turn_color)
        if is_check:
            if len(king_attackers_pos) == 1:
                king_pos = self.board.kings[turn_color].pos
                attacking_piece_pos = king_attackers_pos[0]
                attacking_piece: Piece | 0 = self.board[attacking_piece_pos[1]][attacking_piece_pos[0]]
                if isinstance(attacking_piece, (Knight, Pawn)):
                    possible_spaces_str = [attacking_piece_pos]
                else:
                    # attacking pos method to find all the possible moves?
                    possible_spaces_str = list(map(lambda y: y.cord, list(attacking_piece.attacking_positions_towards_king(king_pos))[:-1]))

        for row in self.board:
            for piece in row:
                if piece == 0:
                    continue
                piece: Piece
                if piece.color != self.turn:
                    continue

                moves = piece.get_possible_moves()
                next(moves, None)
                if self.check and len(self.positions_that_attack_king) == 1 and not isinstance(piece, King):
                    moves = filter(lambda x: x[2:4] in possible_spaces_str, moves)

                yield from moves