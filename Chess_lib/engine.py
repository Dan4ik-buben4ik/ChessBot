import dataclasses
import math
from typing import TypeAlias
import asyncio

from .util import *
from .loader import Board
from .logger import *
from .nn import *


Material: TypeAlias = int
#all in centipawns
PAWN_MATERIAL: Material = 100
KNIGHT_MATERIAL: Material = 300
BISHOP_MATERIAL: Material = 300
ROOK_MATERIAL: Material = 500
QUEEN_MATERIAL: Material = 900

PieceSquareTable: TypeAlias = list
KNIGHT_PST: PieceSquareTable = [
    -5, -4, -3, -2, -2, -3, -4, -5,
    -4, -2,  0,  1,  1,  0, -2, -4,
    -3,  0,  2,  3,  3,  2,  0, -3,
    -2,  1,  3,  4,  4,  3,  1, -2,
    -2,  1,  3,  4,  4,  3,  1, -2,
    -3,  0,  2,  3,  3,  2,  0, -3,
    -4, -2,  0,  1,  1,  0, -2, -4,
    -5, -4, -3, -2, -2, -3, -4, -5
]

BISHOP_PST = [
    -3, -2, -1, -1, -1, -1, -2, -3,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -1,  0,  1,  2,  2,  1,  0, -1,
     0,  1,  3,  4,  4,  3,  1,  0,
     0,  1,  3,  4,  4,  3,  1,  0,
    -1,  0,  1,  2,  2,  1,  0, -1,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -3, -2, -1, -1, -1, -1, -2, -3
]

ROOK_PST = [
     5,  5,  5,  5,  5,  5,  5,  5,
    20, 20, 20, 20, 20, 20, 20, 20,
     0,  0,  0,  5,  5,  0,  0,  0,
     0,  0,  0,  5,  5,  0,  0,  0,
     0,  0,  0,  5,  5,  0,  0,  0,
     0,  0,  0,  5,  5,  0,  0,  0,
    15, 15, 15, 15, 15, 15, 15, 15,
     5,  5,  5,  5,  5,  5,  5,  5
]

QUEEN_PST = [
    -3, -2, -1, -1, -1, -1, -2, -3,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -1,  0,  1,  2,  2,  1,  0, -1,
     0,  1,  3,  4,  4,  3,  1,  0,
     0,  1,  3,  4,  4,  3,  1,  0,
    -1,  0,  1,  2,  2,  1,  0, -1,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -3, -2, -1, -1, -1, -1, -2, -3
]

KING_OPENING_PST = [
     5,  4,  3,  0,  1,  2,  4,  5,
     1,  0, -1, -1, -1, -1,  0,  1,
    -1, -2, -3, -4, -4, -3, -2, -1,
    -2, -3, -4, -5, -5, -4, -3, -2,
    -2, -3, -4, -5, -5, -4, -3, -2,
    -1, -2, -3, -4, -4, -3, -2, -1,
     1,  0, -1, -1, -1, -1,  0,  1,
     5,  4,  3,  0,  1,  2,  4,  5,
]

KING_ENDGAME_PST = [
    -3, -2, -1, -1, -1, -1, -2, -3,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -1,  0,  1,  2,  2,  1,  0, -1,
     0,  1,  3,  4,  4,  3,  1,  0,
     0,  1,  3,  4,  4,  3,  1,  0,
    -1,  0,  1,  2,  2,  1,  0, -1,
    -2, -1,  0,  1,  1,  0, -1, -2,
    -3, -2, -1, -1, -1, -1, -2, -3
]



bishop_pair = 30
doubled_pawn = - 15
isolated_pawn = -20
passed_pawn = 45
mobility = 3
activity_scale = 0.02
king_open_file = -50
rook_open_file = 20
tempo = 10

#transposition table
class TTFlag(enum.Enum):
    __slots__ = ()
    UPPER_BOUND = 0
    LOWER_BOUND = 1
    EXACT = 2


class TTEntree:
    __slots__ = ("depth", "score", "flag", "best_move",)

    def __init__(self, depth, score, flag, best_move):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move

def _move_order_score(board: Board, move: Move, tt_move=None):
    score = 0

    if move == tt_move:
        score += 10

    if board.is_move_check(move):
        score += 5

    if board.is_capture(move):
        score += 3

    if move.promotion:
        score += 2

    return score



def move_ordering(board: Board, moves: list[Move], tt_move=None):
    print("move ordering start")
    board.construct()
    yield from sorted(
        moves,
        key=lambda x: _move_order_score(board, x, tt_move),
        reverse=True
    )


async def async_as_completed(aws):
    done_queue = asyncio.Queue()

    tasks = [asyncio.ensure_future(aw) for aw in set(aws)]

    for task in tasks:
        task.add_done_callback(done_queue.put_nowait)

    for _ in range(len(tasks)):
        yield await done_queue.get()


class ObjectPool:
    def __init__(self, size, object_type):
        if not isinstance(object_type, type):
            raise TypeError("object_type is expected be a type object")

        self._queue = asyncio.Queue()
        self._count = size
        self._type = object_type
        for _ in range(size):
            self._queue.put_nowait(object_type())

    async def borrow_obj(self):
        if self._count == 0:
            new_obj = self._type
            return new_obj()
        self._count -= 1
        return await self._queue.get()

    def return_obj(self, item):
        if not isinstance(item, self._type):
            raise TypeError(f"Expect the item to be of a type {self._type}")
        self._count += 1
        self._queue.put_nowait(item)


async def search(board, alpha, beta, depth, loop, buffer, obj_pool, tt, req_cycle=2):
    entry_move = None
    # checks if the position had already been analysed.
    entry = tt.get(board.hash)
    if entry and entry.depth >= depth:
        entry_move = entry.best_move

        if entry.flag == TTFlag.EXACT:
            return entry.score
        elif entry.flag == TTFlag.LOWER_BOUND:
            alpha = max(alpha, entry.score)
        elif entry.flag == TTFlag.UPPER_BOUND:
            beta = min(beta, entry.score)

        if alpha > beta:
            return entry.score

    # sets up the variables needed post evaluation
    original_alpha = alpha
    original_beta = beta
    color = 1 if board.turn == WHITE else -1
    # if board.outcome() != GameResult.ONGOING:
    #     return EvaluationNNUE.forward(board)[0] * color
    print(f"Searching at depth-until-bottom ({depth})")
    if depth == 1:
        return await evaluate_max_depth(board, -beta, -alpha, loop, buffer, obj_pool, tt) * color
    best = -math.inf
    best_move = None
    board_state = BitBoardState.from_board(board)
    task_buffer = []
    working = True
    move_gen = move_ordering(board, list(board.generate_legal_moves()), entry_move)
    while working:
        print(f"starting a cycle with step: {req_cycle}")
        for _ in range(req_cycle):
            move = next(move_gen, None)
            if move is None:
                working = False
                break

            temp_board = await obj_pool.borrow_obj()
            print(f"Borrowing object {temp_board}")
            temp_board.restore(board_state)

            print(f"trying to push move {move.uci()}")
            temp_board.push(move, add_history=False)
            print(f"pushed move {move.uci()}")

            temp_board.construct()
            task = asyncio.create_task(search(temp_board, -beta, -alpha, depth-1, loop, buffer, obj_pool, tt))
            task.metadata = move.uci()
            task_buffer.append(task)


        print("starting to wait for responce")
        async for next_ready_future in async_as_completed(task_buffer):
            # move = next_ready_future.metadata
            evaluation = await next_ready_future
            print("Got a response")
            evaluation *= color
            if evaluation > best:
                best = evaluation
                best_move = next_ready_future.metadata


            alpha = max(alpha, evaluation)

            if alpha >= beta:
                working = False
                break
        task_buffer.clear()

    best_move = Move.from_uci(best_move)

    # records the position into the table
    if best <= original_alpha:
        flag = TTFlag.UPPER_BOUND
    elif best >= original_beta:
        flag = TTFlag.LOWER_BOUND
    else:
        flag = TTFlag.EXACT

    tt[board.hash] = TTEntree(depth, best, flag, best_move)
    print(f"returning object {board}")
    obj_pool.return_obj(board)


    return best

async def evaluate_max_depth(board, alpha, beta, loop: asyncio.AbstractEventLoop, buffer: asyncio.Queue, obj_pool, tt, req_cycle=5):
    print("Max depth reach")
    entry_move = None
    # checks if the position had already been analysed.
    entry = tt.get(board.hash)
    if entry and entry.depth >= 0:
        entry_move = entry.best_move

        if entry.flag == TTFlag.EXACT:
            return entry.score
        elif entry.flag == TTFlag.LOWER_BOUND:
            alpha = max(alpha, entry.score)
        elif entry.flag == TTFlag.UPPER_BOUND:
            beta = min(beta, entry.score)

        if alpha > beta:
            return entry.score

    result_buffer = []
    print("starting to send requests")
    for move in move_ordering(board, list(board.generate_legal_moves()), entry_move):
        print(f"max depth move ({move.uci()})")
        print()
        board.push(move)
        print("pushed the move")
        future = loop.create_future()
        request = EvaluationNNUE.build_input(board)
        result_buffer.append(future)
        await buffer.put((request, future))
        board.pop()
        print("sent a request")

    print(f"returning object {board}")
    obj_pool.return_obj(board)


    best = -math.inf
    print("starting to wait for the responce")
    for next_ready_future in asyncio.as_completed(result_buffer):
        result = await next_ready_future
        print("working on the futures objects")
        best = max(best, result)

        alpha = max(alpha, result)
        if alpha >= beta:
            break

    return best

async def batch_processor(request_queue: asyncio.Queue, max_batch_size: int, gpu: GPU, timeout:float=0.5):
    # make the batch input to GPU w/o future objects
    batch = []

    while True:
        if not batch:
            # try:
            item = await request_queue.get()
            if item is None:
                request_queue.task_done()
                return
            batch.append(item)
            request_queue.task_done()
            # except asyncio.TimeoutError:
            #     print("buffer is waiting")
            #     print(f"{len(asyncio.all_tasks())} are running")
            #     print(f"batch: {batch}")
            #     raise
            #     await asyncio.sleep(0)

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


async def evaluate(board, alpha, beta, depth, req_cycle=2):
    max_size = 10

    transposition_table = {}
    loop = asyncio.get_running_loop()
    buffer = asyncio.Queue()
    gpu = GPU()
    buffer_task = asyncio.create_task(batch_processor(buffer, max_size, gpu, 0.1))
    obj_pool = ObjectPool(max_size, type(board))

    color = 1 if board.turn == WHITE else -1
    temp_board = await obj_pool.borrow_obj()
    temp_board.copy_from(board)

    res = await search(board, alpha, beta, depth, loop, buffer, obj_pool, transposition_table, req_cycle) * color
    print(f"result = {res}")

    await buffer.put(None)
    await buffer_task


# TODO: make depth incremental (going up by 1)