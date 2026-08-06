from Chess_lib import Board, Piece

from errors import ErroneousDataException

# we try to encode the board from the 2D array of Piece class instances and 0's into 12 layers of board,
# with different pieces marked as 1's and everything else as 0's

# eg, if the board has only white rooks, black rooks, white king and black king, it will yield 8 empty arrays
# and 4 arrays, each with only it's respected piece position marked as 1

# we do that to be able to compress the board into bits, as we don't want to work with multiple output neurons
# which could yield a mixed/error results



class BoardEncoder:
    @staticmethod
    def encode_piece_planes(board: Board) -> list[list[list[0 | 1]]]:
        # planes go from Pawns to Kings in regards to material (Bishop > Knight), first white then black
        # aka the planes:
        planes_dict = {
            "white_pawn": 0,
            "white_knight": 1,
            "white_bishop": 2,
            "white_rook": 3,
            "white_queen": 4,
            "white_king": 5,
            "black_pawn": 6,
            "black_knight": 7,
            "black_bishop": 8,
            "black_rook": 9,
            "black_queen": 10,
            "black_king": 11,

        }
        planes = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(12)]

        for y_i, row in enumerate(board.board):
            for x_i, elem in enumerate(row):
                if isinstance(elem, Piece):
                    # in planes_dict[f"{elem.color}_{elem.name}".lower()] we use the planes_dict
                    # to find the index for the needed plane
                    planes[planes_dict[f"{elem.color}_{elem.name}".lower()]][y_i][x_i] = 1

        return planes

    @staticmethod
    def encode_castling_lines(board) -> list[0 | 1]:
        # converts the castling rights into 1x4 list
        rights = [0, 0, 0, 0]
        pass

    @staticmethod
    def encode_turns(board):
        if board.player == "white":
            return 0
        elif board.player == "black":
            return 1

        raise ErroneousDataException(board.player, "white or black")

    @staticmethod
    def encode_history(board):
        pass

    @staticmethod
    def encode_en_passant(board):
        pass

    @staticmethod
    def encode(board):
        pass
