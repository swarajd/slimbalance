import queue
import threading
from collections import defaultdict

from methods.round_robin import RoundRobinContext
from methods.util import Backend


def rr_thread(ctx, result_queue, loop_count):
    backend_list = []
    for i in range(loop_count):
        backend = ctx.get_next_backend()
        backend_list.append(backend)

    result_queue.put(backend_list)


def test_rr_ctx_none_dead():
    """
    testing the round robin context to make sure
    that it picks each backend equally
    """

    LOOP_COUNT = 10

    # set up backends
    backends = [Backend({"host": f"backend-{x}"}, alive=True) for x in range(3)]

    # create context and queue for results
    test_ctx = RoundRobinContext(backends)
    result_queue = queue.Queue()

    # create threads
    threads = [
        threading.Thread(target=rr_thread, args=(test_ctx, result_queue, LOOP_COUNT))
        for backend in backends
    ]

    # run threads
    for thread in threads:
        thread.start()

    # join threads
    for thread in threads:
        thread.join()

    # gather results
    results = []

    while not result_queue.empty():
        results.extend(result_queue.get())

    # check if the counts for all the hosts are equal
    counts = defaultdict(int)
    for result in results:
        counts[result.host] += 1

    for count in counts.values():
        assert count == LOOP_COUNT


def test_rr_ctx_one_dead():

    """
    testing the round robin context to make sure
    that it picks each REMAINING backend equally (one dead)
    """

    LOOP_COUNT = 10
    DEAD_BACKEND = 2
    EXPECTED_COUNT = 15

    # set up backends
    backends = [Backend({"host": f"backend-{x}"}, alive=True) for x in range(3)]

    backends[DEAD_BACKEND].set_alive(False)

    # create context and queue for results
    test_ctx = RoundRobinContext(backends)
    result_queue = queue.Queue()

    # create threads
    threads = [
        threading.Thread(target=rr_thread, args=(test_ctx, result_queue, LOOP_COUNT))
        for backend in backends
    ]

    # run threads
    for thread in threads:
        thread.start()

    # join threads
    for thread in threads:
        thread.join()

    # gather results
    results = []

    while not result_queue.empty():
        results.extend(result_queue.get())

    # check if the counts for all the hosts are equal
    counts = defaultdict(int)

    for backend in backends:
        counts[backend.host] = 0

    for result in results:
        counts[result.host] += 1

    for idx, count in enumerate(counts.values()):
        if idx == DEAD_BACKEND:
            assert count == 0
        else:
            assert count == EXPECTED_COUNT


def test_rr_ctx_all_dead():

    """
    testing the round robin context to make sure
    that it returns None if no backends are available
    """

    # set up backends
    backends = [Backend({"host": f"backend-{x}"}, alive=False) for x in range(3)]

    # create context and queue for results
    test_ctx = RoundRobinContext(backends)

    backend = test_ctx.get_next_backend()
    assert backend is None
