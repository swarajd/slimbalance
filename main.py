import json
import threading
import time
from functools import partial
from http.server import ThreadingHTTPServer

from backend import Backend
from config import HOSTNAME, PORT
from handler import LoadBalancerHandler
from healthcheck import healthcheck
from methods.ip_hashing import IPHashContext
from methods.least_connections import LeastConnectionsContext
from methods.round_robin import RoundRobinContext


def process_config(config):
    return list(map(Backend, config["backends"]))


def health_checks(backends):
    while True:
        for backend in backends:
            alive = healthcheck(backend.host, backend.port)
            backend.set_alive(alive)
        time.sleep(20)


if __name__ == "__main__":
    # load config
    with open("config.json", "r") as conf:
        config = json.loads(conf.read())

    backends = process_config(config)

    context_dict = {
        "round_robin": RoundRobinContext,
        "ip_hash": IPHashContext,
        "least_connections": LeastConnectionsContext,
    }

    chosen_context_class = context_dict[config["context"]]
    context = chosen_context_class(backends)

    HandlerClass = partial(LoadBalancerHandler, context)

    health_check_thread = threading.Thread(
        target=health_checks, args=(backends,), daemon=True
    )
    health_check_thread.start()

    load_balancer = ThreadingHTTPServer((HOSTNAME, PORT), HandlerClass)
    print(f"Server started: http://{HOSTNAME}:{PORT}")

    try:
        load_balancer.serve_forever()
    except KeyboardInterrupt:
        pass

    load_balancer.server_close()
    print("Server stopped.")
