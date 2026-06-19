from pieces import Piece, Pawn, King, Rook
from position import PositionVector2D


def board_to_FEN(board) -> str:  # board of class loader.Board
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

    if board.player == "white":
        fen += " w"
    else:
        fen += " b"

    # Castling (sections 2 and 3)
    possible_castles = ""
    if board.kings_castle["white"][1]:
        possible_castles += "K"
    if board.kings_castle["white"][0]:
        possible_castles += "Q"
    if board.kings_castle["black"][1]:
        possible_castles += "k"
    if board.kings_castle["black"][0]:
        possible_castles += "q"

    fen += f" {possible_castles if possible_castles else '-'}"

    # en passant
    if board.possible_en_passant:
        fen += f" {board.possible_en_passant.cord}"
    else:
        fen += " -"

    # half moves and full moves
    fen += f" {board.half_moves} {board.full_moves}"

    return fen


def FEN_to_board(fen: str, board):
    print("FEN_to_board")
    print(board)
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
            else:  # modify for board
                piece_colour = "white" if i.isupper() else "black"

                if i.lower() == "p":
                    temp.append(Pawn(board, piece_colour, (x, y)))
                elif i.lower() == "k":
                    temp.append(King(board, piece_colour, (x, y)))
                    board.kings_pos[piece_colour] = PositionVector2D((x, y))
                elif i.lower() == "r":
                    temp.append(Rook(board, piece_colour, (x, y)))
                # else:
                #     temp.append(i)
                x += 1
        board.board.append(temp)

    # colour
    if sections[1] == "w":
        board.player = "white"
    if sections[1] == "b":
        board.player = "black"

    # castling
    castles = sections[2]
    if castles == "-":
        board.kings_castle["white"] = [False, False]
        board.kings_castle["black"] = [False, False]
    elif "K" in castles:
        board.kings_castle["white"][1] = True
    elif "Q" in castles:
        board.kings_castle["white"][0] = True
    elif "k" in castles:
        board.kings_castle["black"][1] = True
    elif "q" in castles:
        board.kings_castle["black"][0] = True


    #### Havent added to the board. WIll decide later
    # en passant
    board.possible_en_passant = PositionVector2D(sections[3]) if sections[3] != "-" else None

    # half moves and full moves
    board.half_moves = sections[4]
    board.full_moves = sections[5]

    # print("\nFEN OUTPUT")
    # print(board.player)
    # print(board.kings_castle)
    # print(board.possible_en_passant)
    # print(board.half_moves)
    # print(board.full_moves)
    # print()

    print(f"board: {board.board}")


    return

def validate_FEN(fen: str) -> bool:
    # aka if castling conditions are met with rooks and king's position
    # also with the pawn positions for the en passant
    pass


board = [[0, 0, 0, 0, "k", 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, "K", 0, 0, 0]]
# starting pos: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

# n = FEN_to_board("4k3/8/8/8/8/8/8/4K3 w KQkq - 0 1")
# print(n)
# f = list_to_FEN(n)
# print(f)
# print(f == n)
