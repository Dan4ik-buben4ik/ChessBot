from pieces import Piece, Pawn, King, Rook, Bishop, Queen, Knight
from position import PositionVector2D


def board_to_FEN(board) -> str:  # board of class loader.Board
    """ a function to translate a chess position from the board class object into FEN string (Forsyth-Edwards Notation)

    :param board: an instance of the loader.Board class
    :type board: loader.Board

    :return: a chess position formatted in FEN
    :rtype: str
    """



    fen = ""

    # --DEBUG--
    # print("\nFEN INPUT")
    # print(board.player)
    # print(board.kings_castle)
    # print(board.possible_en_passant)
    # print(board.half_moves, board.full_moves)
    # print()

    # Positions (section 1)
    for row in board.board:
        space = 0
        for piece in row:
            if piece != 0:  # isinstance later
                if space != 0:
                    fen += str(space)
                    space = 0

                fen += piece.sym
            else:
                space += 1
        if space != 0:
            fen += str(space)
        fen += "/"
    fen = fen[:-1]

    if board.turn == "white":
        fen += " w"
    else:
        fen += " b"

    # Castling (sections 2 and 3)
    possible_castles = ""
    if board.castling_rights["white"][1]:
        possible_castles += "K"
    if board.castling_rights["white"][0]:
        possible_castles += "Q"
    if board.castling_rights["black"][1]:
        possible_castles += "k"
    if board.castling_rights["black"][0]:
        possible_castles += "q"

    fen += f" {possible_castles if possible_castles else '-'}"

    # en passant
    if board.possible_en_passant:
        fen += f" {board.possible_en_passant.algebraic}"
    else:
        fen += " -"

    # half moves and full moves
    fen += f" {board.half_moves} {board.full_moves}"

    return fen


def FEN_to_board(fen: str, board):
    """ A function to translate a chess position in the FEN (Forsyth-Edwards Notation)
     and transcript into an instance of a board class, modifying it in place

    :param fen: the chess position in the FEN string that gets translated
    :type fen: str

    :param board: an instance of the board where the information gets written
    :type board: loader.Board
    """
    board.board = []


    sections = fen.split(" ")

    # position (section 1)
    for y, row in enumerate(sections[0].split("/")):
        temp = []
        x = 0
        for i in row:
            if i.isnumeric():
                temp.extend([0] * int(i))
                x += int(i)
            else:
                piece_colour = "white" if i.isupper() else "black"

                if i.lower() == "p":
                    temp.append(Pawn(board, piece_colour, (x, y)))
                elif i.lower() == "k":
                    king = King(board, piece_colour, (x, y))
                    temp.append(king)
                    board.kings[piece_colour] = king
                elif i.lower() == "q":
                    temp.append(Queen(board, piece_colour, (x, y)))
                elif i.lower() == "r":
                    temp.append(Rook(board, piece_colour, (x, y)))
                elif i.lower() == "b":
                    temp.append(Bishop(board, piece_colour, (x, y)))
                elif i.lower() == "n":
                    temp.append(Knight(board, piece_colour, (x, y)))
                # else:
                #     temp.append(i)
                x += 1
        board.board.append(temp)

    # colour
    if sections[1] == "w":
        board.turn = "white"
    if sections[1] == "b":
        board.turn = "black"

    # castling
    castles = sections[2]
    if castles == "-":
        board.castling_rights["white"] = [False, False]
        board.castling_rights["black"] = [False, False]
    if "K" in castles:
        board.castling_rights["white"][1] = True
    if "Q" in castles:
        board.castling_rights["white"][0] = True
    if "k" in castles:
        board.castling_rights["black"][1] = True
    if "q" in castles:
        board.castling_rights["black"][0] = True

    # en passant
    board.possible_en_passant = PositionVector2D(sections[3]) if sections[3] != "-" else None

    # half moves and full moves
    board.half_moves = int(sections[4])
    board.full_moves = int(sections[5])

    # print("\nFEN OUTPUT")
    # print(board.player)
    # print(board.kings_castle)
    # print(board.possible_en_passant)
    # print(board.half_moves)
    # print(board.full_moves)
    # print()

    king = board.kings[board.turn]
    is_check, attacking_pos = board.check_if_pos_attacked(king.pos, board.turn)
    print(is_check, attacking_pos)
    if is_check:
        board.check = True
        board.positions_that_attack_king = attacking_pos




def validate_FEN(fen: str) -> bool:
    """ A function to validate the FEN (Forsyth-Edwards Notation) format standards of a string fen

    :param fen: a chess position in the FEN format that is getting validated
    :type fen: str

    :return: returns whether the string is a proper FEN string
    :rtype: bool
    """

    #TODO: finish the function
    # aka if castling conditions are met with rooks and king's position
    # also with the pawn positions for the en passant

    sections = fen.split(" ")
    if len(sections) != 6:
        return False


    if "k" not in sections[0] or "K" not in sections[0]:
        return False

    rows = sections[0].split("/")
    if len(rows) != 8:
        return False

    for r in rows:
        total = 0
        for i in r:
            if i.isnumeric():
                total += int(i)
            elif i.lower() in ("k", "q", "r", "b", "n", "p"):
                total += 1
            else:
                return False
        if total != 8:
            return False

    if sections[1] not in ("b", "w"):
        return False

    if not (sections[2] == "-" or all(c.lower() in ("k", "q") for c in sections[2])):
        #TODO: validate with the rooks and kings for the castling
        return False

    if not(sections[3] == "-" or PositionVector2D.is_algebraic(sections[3])):
        return False

    if not sections[4].isnumeric() or not sections[5].isnumeric():
        return False

    return True


