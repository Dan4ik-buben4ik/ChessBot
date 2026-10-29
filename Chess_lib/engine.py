import dataclasses
import math
from typing import TypeAlias
import asyncio

from .loader import Board
from .nn import *



#transposition table


class TTFlag(enum.Enum):
    # TODO: change to type allias
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

    if board.is_move_check(move): # TODO: make lazy, so no push/pop
        score += 5

    if board.is_capture(move):
        score += 3

    if move.promotion:
        score += 2

    return score



def move_ordering(board: Board, moves: list[Move], tt_move=None):
    moves = sorted(
        moves,
        key=lambda x: _move_order_score(board, x, tt_move),
        reverse=True
    )
    print(moves)
    yield from moves


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


class SearchLogger:
    data = {
        "root": {"moves": [], "move evaluations": [], "evaluation": 0, "depth": 0}
    }
    nodes = 0


    def log_intro(self, root, move: str, depth):
        self.nodes += 1
        new_path = f"{root}/{move}"
        self.data[root]["moves"].append(move)
        self.data[root]["depth"] = depth

        self.data[new_path] = {"moves": [], "move evaluations": [], "evaluation": 0, "depth": 0}
        return new_path

    def log_outro(self, path, evaluation):
        new_path = "/".join(path.split("/")[:-1])
        self.data[path]["evaluation"] = evaluation
        if new_path:
            self.data[new_path]["move evaluations"].append(evaluation)


    def print_dict(self):
        import json
        with open("log.txt", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.data, indent=4))
            file.write("\n")
            file.flush()
        # print(json.dumps(self.data, indent=4))

    def view_dict(self):
        try:
            path = input("\nInput the path to check the values: ")
            temp = self.data[path]
            print(f"path: {path}")
            print(f"moves: {temp['moves']}")
            print(f"path evaluation: {temp['evaluation']}")
            print(f"move evaluations: {temp['move evaluations']}")
            print(f"depth: {temp['depth']}")
        except BaseException:
            print("There is no such path")


async def search(board, alpha, beta, depth, loop, buffer, obj_pool, tt, req_cycle=2, *, logger: SearchLogger, root: str="root"):
    color = 1 if board.turn == WHITE else -1
    outcome = board.outcome()
    if outcome == GameResult.CHECKMATE:
        return INF * color
    elif outcome != GameResult.ONGOING:
        return 0

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
        return await evaluate_max_depth(board, -beta, -alpha, loop, buffer, tt, req_cycle, logger=logger, root=root) * color
    best = -INF
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
            # logging logic
            branch = logger.log_intro(root, move.uci(), depth)

            temp_board = await obj_pool.borrow_obj()
            print(f"Borrowing object {temp_board}")
            temp_board.restore(board_state)

            # print(f"trying to push move {move.uci()}")
            temp_board.push(move, add_history=False)
            print(f"pushed move {move.uci()}")

            temp_board.construct()
            task = asyncio.create_task(search(temp_board, -beta, -alpha, depth-1, loop, buffer, obj_pool, tt, req_cycle=req_cycle, logger=logger, root=branch))
            task.metadata = move.uci()
            task_buffer.append(task)


        # print("starting to wait for responce")
        async for next_ready_future in async_as_completed(task_buffer):
            # move = next_ready_future.metadata
            evaluation = await next_ready_future

            # print("Got a response")
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
    logger.log_outro(root, best)

    # records the position into the table
    if best <= original_alpha:
        flag = TTFlag.UPPER_BOUND
    elif best >= original_beta:
        flag = TTFlag.LOWER_BOUND
    else:
        flag = TTFlag.EXACT

    tt[board.hash] = TTEntree(depth, best, flag, best_move)
    # print(f"returning object {board}")
    obj_pool.return_obj(board)


    return best

async def evaluate_max_depth(board, alpha, beta, loop: asyncio.AbstractEventLoop, buffer: asyncio.Queue, tt, req_cycle=1, *, logger: SearchLogger, root: str):
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

    best = -INF
    working = True
    result_buffer = []
    move_gen = move_ordering(board, list(board.generate_legal_moves()), entry_move)
    # print("starting to send requests")
    while working:
        print(f"starting a cycle with step: {req_cycle}")
        for _ in range(req_cycle):
            move = next(move_gen, None)
            if move is None:
                working = False
                break
            # logging logic
            # branch = logger.log_intro(root, move.uci(), depth)

            # print(f"trying to push move {move.uci()}")
            print(f"max depth move ({move.uci()})")
            print()
            board.push(move)

            request = EvaluationNNUE.build_input(board)
            future = loop.create_future()
            future.metadata = move.uci()

            result_buffer.append(future)
            await buffer.put((request, future))
            board.pop()
    # print("starting to wait for the responce")
        async for next_ready_future in async_as_completed(result_buffer):
            result = await next_ready_future
            print(f"got result for move: {next_ready_future.metadata}")
            # print("working on the futures objects")
            print(result)
            best = max(best, result)

            alpha = max(alpha, best)
        if alpha >= beta:
            break
    logger.log_outro(root, best)
    print("quit max depth")
    return best

async def batch_processor(request_queue: asyncio.Queue, max_batch_size: int, gpu: GPU, timeout:float=0.5):
    # make the batch input to GPU w/o future objects
    batch = []

    while True:
        if not batch:
            # try:
            print("\nwaiting for request_queue")
            loop = asyncio.get_running_loop()
            print(asyncio.all_tasks(loop))
            print(batch)
            print()
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
                    print("None is passed, done")
                    request_queue.task_done()
                    if batch:
                        results = await gpu.evaluate(batch, len(batch))
                        print("got results from gpu")
                        for item, res in zip(batch, results):
                            _, future = item
                            future.set_result(res)
                            print(future.metadata)
                        print("set results to futures")
                    return

                batch.append(item)
                request_queue.task_done()

            except asyncio.TimeoutError:
                break

        print(f"len batch is < {max_batch_size} ({len(batch)})")
        if batch:
            print(f"is batch empty: {batch == []}")
            results = await gpu.evaluate(batch, len(batch))
            print("gpu had evaluated")
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


async def evaluate(board, alpha, beta, depth, req_cycle=1):
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
    logger = SearchLogger()
    res = await search(board, alpha, beta, depth, loop, buffer, obj_pool, transposition_table, req_cycle, logger=logger) * color
    print(f"result = {res}")

    print("\nputting None")
    await buffer.put(None)
    await buffer_task

    # for _ in range(3):
    #     logger.view_dict()


# TODO: make depth incremental (going up by 1)

async def best_move_cpu(board, depth):
    alpha = -INF
    beta = INF
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
    logger = SearchLogger()
    eval = await search(board, alpha, beta, depth, loop, buffer, obj_pool, transposition_table, logger=logger) * color
    print("finish searching")
    await buffer.put(None)
    await buffer_task

    if transposition_table.get(board.hash, None):
        best_move = transposition_table.get(board.hash, None).best_move
    else:
        best_move = None

    return best_move, eval




