def _move_order_score(board, move, tt_move=None):
    score = 0

    if move == tt_move:
        score += 10

    if board.is_move_check(move):
        score += 5

    if board.is_move_capture(move):
        score += 3

    if move.promotion:
        score += 2

    return score


def order_moves(board, moves, tt_move=None):
    return sorted(
        moves,
        key=lambda x: _move_order_score(board, x, tt_move),
        reverse=True
    )