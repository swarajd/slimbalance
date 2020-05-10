import json
import threading
import time
from functools import partial
from http.server import ThreadingHTTPServer

from config import HOSTNAME, PORT
from healthcheck import healthcheck
from methods.round_robin import RoundRobinContext
from methods.util import LoadBalancerHandler, process_config


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

    rr_context = RoundRobinContext(backends)

    HandlerClass = partial(LoadBalancerHandler, rr_context)

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
