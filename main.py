from Chess_lib import *
from Chess_lib.util import *
from Chess_lib.nn import *
from Chess_lib.nn_maths import *
from Chess_lib.engine import Engine, logger


# only queens and kings: "3qk3/8/8/8/8/8/8/3QK3 w - - 0 1"
# only rooks and kings: r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1  hash = 8443997070231762362
# only bishops and kings: 2b1kb2/8/8/8/8/8/8/2B1KB2 w - - 0 1
# only knights and kings:1n2k1n1/8/8/8/8/8/8/1N2K1N1 w - - 0 1
# en_passant check: "4k3/8/8/8/1p6/8/P7/4K3 w - - 0 1"
# discovered-check check: 4k3/8/8/8/8/5p2/4P3/K3R3 w - - 0 1
# double check: "8/8/8/8/4k3/5p2/4P3/K3R3 w - - 0 1"
# all pawns on the last row: "2R5/PPPPPPPP/8/8/8/8/8/k6K w - - 0 1"
# starting position: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# diagonal pin : "4k3/8/8/8/7q/8/5N2/4K3 w KQkq - 0 1"
# empty : "8/8/8/8/8/8/8/8 w - - 0 1"

# bit_board = Board.from_fen("3k3r3/8/8/8/8/8/8/R3K3 w - - 0 1")
# bit_board.construct()
#
# # PLAN
# # - half kp set up
# # - pgn
#
#
#
# while True:
#     legal = list(bit_board.generate_legal_moves())
#     print("possible moves")
#     print(legal)
#
#     move = bit_board.parse_san(input("san: "))
#     bit_board.push(move)
#     bit_board.construct()
#     print(bit_board.outcome())

#
# bit_board = Board.from_fen("r2k4/8/8/8/8/8/8/R3K3 b - - 0 1")
# engine = Engine(bit_board, 100, -100, 10)
#
# best_move = engine.generate()
# print("best move")
# print(best_move)
# # print(len(logger.data.keys()))


# task to make a buffer that sends batches of size MAX SIZE in a function send_request
#
import time
import random
import math
import asyncio
import collections


"""
- minmax reaches the leaf, creating a local trail of bitboard states
- when reaching the leaf, it sends an evaluation request to buffer
- as well as the current board state object?
- when buffer is full, it halts minmax and sends the batch to the GPU
- GPU evaluates it and returns the evaluations to the leaves
- the issues is that when the evaluation is returned, the engine would already check a position that is 1-2 moves different.
  Possible solution is to store a move trail and update the tree manually??? how to do that?
"""

class Board:
    moves = []
    def push(self, move):
        self.moves.append(move)
        print(f"\nPushed a move {move}")
    def pop(self):
        self.moves.pop()
        print(f"Popped the last move\n")
    def copy(self):
        return sum(self.moves)

def move_gen():
    yield from [random.randint(1, 10000) for _ in range(random.randint(1, 20))]


class GPU:
    @staticmethod
    async def evaluate(batch, length):
        print("Processing Requests")
        await asyncio.sleep(2)
        print("Finished Processing Requests")
        return [random.random() for _ in range(length)]

async def search(board, depth, loop, buffer):
    if depth == 1:
        return await evaluate_max_depth(board, loop, buffer)
    print(f"Searching at depth-until-bottom ({depth})")
    best = -math.inf
    for move in move_gen():
        board.push(move)
        eval = await search(board, depth-1, loop, buffer)
        board.pop()

        best = max(eval, best)
    return best

async def evaluate_max_depth(board, loop: asyncio.AbstractEventLoop, buffer: asyncio.Queue):
    print("reach max depth")
    result_buffer = []
    for move in move_gen():
        board.push(move)
        future = loop.create_future()
        request = board.copy()
        result_buffer.append(future)
        await buffer.put((request, future))
        board.pop()

    best = -math.inf
    print("waiting for results")
    for next_ready_future in asyncio.as_completed(result_buffer):
        result = await next_ready_future
        best = max(best, result)
    print("got all results")
    return best

async def batch_processor(request_queue: asyncio.Queue, max_batch_size: int, gpu: GPU, timeout:float=2):
    batch = []

    while True:
        if not batch:
            item = await request_queue.get()
            if item is None:
                request_queue.task_done()
                return
            batch.append(item)
            request_queue.task_done()

        while len(batch) < max_batch_size:
            try:
                item = await asyncio.wait_for(request_queue.get(), timeout=timeout)
                if item is None:
                    request_queue.task_done()
                    if batch:
                        results = await gpu.evaluate(batch, len(batch))
                        print("got results from gpu")
                        for item, res in zip(batch, results):
                            _, future = item
                            future.set_result(res)
                        print("set results to futures")
                    return

                batch.append(item)
                request_queue.task_done()

            except asyncio.TimeoutError:
                break

        if batch:
            results = await gpu.evaluate(batch, len(batch))
            print("got results from gpu")
            for item, res in zip(batch, results):
                _, future = item
                future.set_result(res)
                # if not future.done():
                #     # call_soon не переключает контекст на клиента мгновенно.
                #     # Он просто регистрирует событие завершения. Воркер спокойно дойдет до конца цикла!
                #     loop.call_soon(future.set_result, res)
            print("set results to futures")
            batch = []


async def evaluate_board():
    max_size = 10
    loop = asyncio.get_running_loop()
    buffer = asyncio.Queue(max_size)
    gpu = GPU()
    buffer_task = asyncio.create_task(batch_processor(buffer, max_size, gpu, 0.5))

    board = Board()
    res = await search(board, 1, loop, buffer)
    print(f"result = {res}")

    await buffer.put(None)
    await buffer_task


# need a way to segregate by 5s
start = time.time()
asyncio.run(evaluate_board())
end = time.time()
print(f"took {end-start:.2f} sec")




