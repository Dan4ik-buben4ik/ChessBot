from loader import *
# only rooks and kings: r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1
# en_passant check: "4k3/8/8/8/1p6/8/P7/4K3 w KQkq - 0 1"
board = Board(fen="r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
board.construct()
board.move()
board.construct()
board.move()
board.construct()
board.move()
board.construct()
board.move()
board.construct()
board.move()
board.construct()
board.move()
board.construct()
board.move()
board.construct()
board.move()
board.construct()

