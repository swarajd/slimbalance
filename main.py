from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection
import json
from functools import partial

from methods.round_robin import RoundRobinContext, RoundRobinHandler

# some sane defaults
HOSTNAME = "localhost"
PORT     = 8080

if __name__ == "__main__":
    # load config
    with open("config.json", "r") as conf:
        config = json.loads(conf.read())

    rr_context = RoundRobinContext(config)

    HandlerClass = partial(RoundRobinHandler, rr_context)

    load_balancer = ThreadingHTTPServer((HOSTNAME, PORT), HandlerClass)
    print(f"Server started: http://{HOSTNAME}:{PORT}")

    try:
        load_balancer.serve_forever()
    except KeyboardInterrupt:
        pass

    load_balancer.server_close()
    print("Server stopped.")