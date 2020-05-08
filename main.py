import json
import socket
import threading
import time
from functools import partial
from http.server import ThreadingHTTPServer

from config import HOSTNAME, PORT
from methods.round_robin import RoundRobinContext, RoundRobinHandler
from methods.util import process_config

def healthcheck(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RD)
        return True
    except socket.timeout:
        return False
    except OSError:
        return False


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

    HandlerClass = partial(RoundRobinHandler, rr_context)

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
