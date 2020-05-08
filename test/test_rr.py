import threading
import queue
from collections import defaultdict
from methods.round_robin import RoundRobinContext
from methods.util import Backend

LOOP_COUNT = 10

def rr_thread(ctx, result_queue):
    backend_list = []
    for i in range(LOOP_COUNT):
        backend = ctx.get_next_backend()
        backend_list.append(backend)

    result_queue.put(backend_list)
    

def test_rr_ctx():

    # set up backends
    backend_ids = [
        'a', 'b', 'c'
    ]

    backends = [
        Backend({
            'host': id
        })
        for id in backend_ids
    ]

    for backend in backends:
        backend.set_alive(True)

    # create context and queue for results
    test_ctx = RoundRobinContext(backends)
    result_queue = queue.Queue()

    # create threads
    threads = [
        threading.Thread(
            target=rr_thread,
            args=(test_ctx,result_queue)
        ),
        threading.Thread(
            target=rr_thread,
            args=(test_ctx,result_queue)
        ),
        threading.Thread(
            target=rr_thread,
            args=(test_ctx,result_queue)
        )
    ]

    # run threads
    for thread in threads:
        thread.start()

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
