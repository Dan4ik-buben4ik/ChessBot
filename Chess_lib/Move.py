from position import PositionVector2D
from util import TurnColor


def find_san_pieces(board, symbol: str, new_pos: PositionVector2D) -> list:
    result_pieces = []
    for row in board.board:
        for piece in row:
            if piece == 0:
                continue
            elif piece.sym.lower() != symbol.lower():
                continue
            elif piece.color != board.turn:
                continue
            if piece.reach_check(new_pos):
                if not piece.blocking_check(new_pos):
                    result_pieces.append(piece)
    return result_pieces


def uci_to_san(board, move: str) -> str:
    # eg. e2e4 -> e4 or g1f3 -> Nf3 or e7e8q -> e8=Q or a1d1 -> Ra1d1
    init_pos = PositionVector2D(move[:2])
    new_pos = PositionVector2D(move[2:4])
    try:
        promotion = move[4]
    except IndexError:
        promotion = None

    piece = board.board[init_pos[1]][init_pos[0]]
    possible_pieces = find_san_pieces(board, piece.sym, new_pos)
    pos_change = new_pos - init_pos
    # check if it is en passant
    if len(possible_pieces) == 1 and piece.name == "Pawn" and abs(pos_change[0]) == 1 and pos_change[
        1] == piece.moving_direction:
        return f"{init_pos.algebraic[0]}x{new_pos.algebraic}"

    # check if its castling
    if piece.name == "King" and abs(pos_change[0]) == 2:
        return "O-O" if pos_change[0] > 0 else "O-O-O"

    # if len(possible_pieces) == 1:
    #     return f"{piece.sym.capitalize()}{new_pos.cord}{promotion if promotion else ''}"

    possible_prefix = []
    for cord in possible_pieces:
        if cord.pos == init_pos:
            continue
        possible_prefix.extend((cord.pos.algebraic[0], cord.pos.algebraic[1]))

    prefix = ""
    if init_pos.algebraic[1] in possible_prefix:
        prefix = prefix + init_pos.algebraic[0]
    if init_pos.algebraic[0] in possible_prefix:
        prefix = prefix + init_pos.algebraic[1]

    # check for captures
    if board.board[new_pos[1]][new_pos[0]] != 0:
        prefix = prefix + "x"

    return f"{piece.sym.capitalize() if not piece.name == 'Pawn' else ''}{prefix}{new_pos.algebraic}{promotion if promotion else ''}"


def san_to_uci(board, move: str) -> str:
    if move == "O-O":
        return "e1g1" if board.player == "white" else "e8g8"
    elif move == "O-O-O":
        return "e1c1" if board.player == "white" else "e8c8"

    if move[0] not in ("Q", "K", "R", "N", "B", "P"):
        move = "".join(("P", move))

    try:
        move, promotion = move.split("=")
    except ValueError:
        promotion = None

    try:
        move = "".join(move.split("x"))
    except ValueError:
        pass

    piece_sym = move[0]
    new_pos = PositionVector2D(move[-2:])

    # logic to get the initial position
    possible_pieces = find_san_pieces(board, piece_sym, new_pos)

    if len(possible_pieces) == 1:
        return f"{possible_pieces[0].pos.cord}{new_pos.algebraic}{promotion if promotion else ''}"

    # finding prefix
    if len(move) == 5:
        return f"{move[1:3]}{new_pos.algebraic}{promotion if promotion else ''}"
    elif len(move) == 4:
        prefix = move[1]

    for piece in possible_pieces:
        if prefix in piece.pos.cord:
            init_pos = piece.pos

    return f"{init_pos.algebraic}{new_pos.algebraic}{promotion if promotion else ''}"


def uci_decoder(uci_move: str):
    init_pos = PositionVector2D(uci_move[:2])
    new_pos = PositionVector2D(uci_move[2:4])

    try:
        promotion = uci_move[4].upper()
    except IndexError:
        promotion = None

    return init_pos, new_pos, promotion


def uci_encoder(init_pos: PositionVector2D, new_pos: PositionVector2D, promotion=None) -> str:
    return "".join((init_pos.algebraic, new_pos.algebraic, promotion.lower() if promotion else ""))


class Move:
    def __init__(self, init_pos, new_pos, promotion):
        self.init_pos = init_pos
        self.final_pos = new_pos
        self._promotion = promotion
        # self.move_type

    # @property
    # def is_capture(self):
    #     return
    #
    # @property
    # def is_castle(self):
    #     return
    #
    # @property
    # def is_en_passant(self):
    #     if self.piece.name == "Pawn" and abs(self.final_pos - self.init_pos)[0] == 1 and self.final_pos == self.board.possible_en_passant:
    #         return True
    #     return False
    #
    @property
    def promotion(self):
        if self._promotion:
            return self._promotion
        return False

    @property
    def pos_change(self):
        return self.final_pos - self.init_pos

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.init_pos == other.init_pos and self.final_pos == other.final_pos and self.promotion == other.promotion

    @classmethod
    def from_uci(cls, uci_move_txt):
        init_pos = PositionVector2D.from_algebraic(uci_move_txt[:2])
        final_pos = PositionVector2D.from_algebraic(uci_move_txt[2:4])

        if len(uci_move_txt) == 5:
            promotion = uci_move_txt[4]
        else:
            promotion = None

        return cls(init_pos, final_pos, promotion)

    def to_uci(self):
        return "".join((self.init_pos.algebraic, self.final_pos.algebraic, self.promotion if self.promotion else ""))

    @classmethod
    def from_san(cls, board, san_move_txt):
        if san_move_txt == "O-O":
            uci = "e1g1" if board.player == TurnColor.WHITE else "e8g8"
            init_pos = PositionVector2D.from_algebraic(uci[:2])
            final_pos = PositionVector2D.from_algebraic(uci[2:4])
            return cls(init_pos, final_pos, None)
        elif san_move_txt == "O-O-O":
            uci = "e1c1" if board.player == TurnColor.WHITE else "e8c8"
            init_pos = PositionVector2D.from_algebraic(uci[:2])
            final_pos = PositionVector2D.from_algebraic(uci[2:4])
            return cls(init_pos, final_pos, None)

        if san_move_txt[0] not in ("Q", "K", "R", "N", "B", "P"):
            san_move_txt = "".join(("P", san_move_txt))

        try:
            san_move_txt, promotion = san_move_txt.split("=")
            promotion = promotion.lower()
        except ValueError:
            promotion = None

        try:
            san_move_txt = "".join(san_move_txt.split("x"))
        except ValueError:
            pass

        piece_sym = san_move_txt[0]
        final_pos = PositionVector2D.from_algebraic(san_move_txt[-2:])
        possible_pieces = find_san_pieces(board, piece_sym, final_pos)

        if len(possible_pieces) == 1:
            return cls(possible_pieces[0].pos, final_pos, promotion)

        # finding prefix
        if len(san_move_txt) == 5:
            prefix = san_move_txt[1:3]
        elif len(san_move_txt) == 4:
            prefix = san_move_txt[1]

        for piece in possible_pieces:
            if prefix in piece.pos.cord:
                init_pos = piece.pos

        return cls(init_pos, final_pos, promotion)


    def to_san(self, board):
        """
        IN docs write how it is a board dependant function, thus after the move is made, it cant be used
        """


        piece = board.board[self.init_pos[1]][self.init_pos[0]]
        possible_pieces = find_san_pieces(board, piece.sym, self.final_pos)
        pos_change = self.final_pos - self.init_pos
        # check if it is en passant
        if len(possible_pieces) == 1 and piece.name == "Pawn" and abs(pos_change[0]) == 1 and pos_change[1] == piece.moving_direction:
            return f"{self.init_pos.algebraic[0]}x{self.final_pos.algebraic}"

        # check if its castling
        if piece.name == "King" and abs(pos_change[0]) == 2:
            return "O-O" if pos_change[0] > 0 else "O-O-O"


        possible_prefix = []
        for cord in possible_pieces:
            if cord.pos == self.init_pos:
                continue
            possible_prefix.extend((cord.pos.algebraic[0], cord.pos.algebraic[1]))

        prefix = ""
        if self.init_pos.algebraic[1] in possible_prefix:
            prefix = prefix + self.init_pos.algebraic[0]
        if self.init_pos.algebraic[0] in possible_prefix:
            prefix = prefix + self.init_pos.algebraic[1]

        # check for captures
        if board.board[self.final_pos[1]][self.final_pos[0]] != 0:
            prefix = prefix + "x"

        return f"{piece.sym.capitalize() if not piece.name == 'Pawn' else ''}{prefix}{self.final_pos.algebraic}{self._promotion if self._promotion else ''}"

    def __repr__(self):
        return self.to_uci()



