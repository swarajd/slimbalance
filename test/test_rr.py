import threading
import queue
from collections import defaultdict
from methods.round_robin import RoundRobinContext
from methods.util import Backend

def rr_thread(ctx, result_queue, loop_count):
    backend_list = []
    for i in range(loop_count):
        backend = ctx.get_next_backend()
        backend_list.append(backend)

    result_queue.put(backend_list)
    

"""
testing the round robin context to make sure
that it picks each backend equally
"""
def test_rr_ctx_none_dead():

    LOOP_COUNT = 10

    # set up backends
    backends = [Backend({'host': f"backend-{x}"}, alive=True) for x in range(3)]

    # create context and queue for results
    test_ctx = RoundRobinContext(backends)
    result_queue = queue.Queue()

    # create threads
    threads = [
        threading.Thread(
            target=rr_thread,
            args=(test_ctx,result_queue,LOOP_COUNT)
        )
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
