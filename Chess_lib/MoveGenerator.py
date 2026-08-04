from types import GeneratorType

from pieces import Piece, Knight, Pawn, King


def generate_legal_moves(board) -> GeneratorType:
    """ The main function to generate the possible moves in a given position

    :param board: the chess position in which the function generated the moves
    :type board: loader.Board

    :return: A generator that yields string moves formatted in UCI notation
    :rtype: collections.abc.Generator[move.Move]
    """
    is_check, king_attackers_pos = board.check_if_king_attacked(board.turn)
    if is_check:
        if len(king_attackers_pos) == 1:
            king_pos = board.kings[board.turn].pos
            attacking_piece_pos = king_attackers_pos[0]
            attacking_piece: Piece | 0 = board.board[attacking_piece_pos[1]][attacking_piece_pos[0]]
            if isinstance(attacking_piece, (Knight, Pawn)):
                possible_spaces_str = [attacking_piece_pos]
            else:
                # attacking pos method to find all the possible moves?
                possible_spaces_str = list(attacking_piece.attacking_positions_towards_king(king_pos))[:-1]

    for row in board.board:
        for piece in row:
            if piece == 0:
                continue
            piece: Piece
            if piece.color != board.turn:
                continue

            moves = piece.get_possible_moves()
            next(moves, None)
            if is_check and len(king_attackers_pos) == 1 and not isinstance(piece, King):
                moves = filter(lambda x: x.final_pos in possible_spaces_str, moves)

            yield from moves


def generate_quiescence_legal_moves(board):
    """ The function to generate all the quiescence (calm) moves

        we generate normal legal moves and filter those that either capture something or give a check

        *Note: quiescence move is a move that isn't a capture nor a check*

        :param board: the chess position in which the function generated the moves
        :type board: loader.Board

        :return: A generator that yields string moves formatted in UCI notation
        :rtype: collections.abc.Generator[move.Move]
        """
    legal_moves = generate_legal_moves(board)
    yield from filter(lambda x: not (board.is_move_capture(x) or board.is_move_check(x)), legal_moves)




