from backend import Backend
from methods.ip_hashing import IPHashContext


def test_ip_hash_ctx_none_dead():
    """
    testing the IP hash context to make sure
    that it picks the correct backend based on the hash
    """

    backends = [Backend({"host": f"backend-{x}"}, alive=True) for x in range(3)]

    ip_addrs = [
        "127.0.0.1",  # hashes to 0 mod 3
        "127.0.0.10",  # hashes to 1 mod 3
        "127.0.0.3",  # hashes to 2 mod 3
    ]

    contexts = [{"address": (ip_addr, 80)} for ip_addr in ip_addrs]

    # create context and check if the correct backend is chosen
    test_ctx = IPHashContext(backends)

    for idx, context in enumerate(contexts):
        cur_backend = test_ctx.get_next_backend(contexts[idx])
        assert cur_backend == backends[idx]


def test_ip_hash_ctx_one_dead():
    """
    testing the IP hash context to make sure it picks
    the next best context if the chosen hashed backend is dead
    """

    backends = [Backend({"host": f"backend-{x}"}, alive=True) for x in range(3)]

    DEAD_BACKEND = 0

    backends[DEAD_BACKEND].set_alive(False)

    context = {"address": ("127.0.0.2", 80)}  # hashes to 0 mod 3

    # create context and check if the correct backend is chosen
    test_ctx = IPHashContext(backends)

    cur_backend = test_ctx.get_next_backend(context)
    assert cur_backend == backends[DEAD_BACKEND + 1]


def test_ip_hash_ctx_all_dead():

    """
    testing the ip hashing context to make sure
    that it returns None if no backends are available
    """

    # set up backends
    backends = [Backend({"host": f"backend-{x}"}, alive=False) for x in range(3)]

    # create context
    test_ctx = IPHashContext(backends)

    # dummy context
    context = {"address": ("127.0.0.1", 80)}

    backend = test_ctx.get_next_backend(context)
    assert backend is None
