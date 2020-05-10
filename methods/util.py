import abc
import threading
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler


class Context(abc.ABC):
    @abc.abstractmethod
    def get_next_backend(self):
        """
        get the next backend based on the context
        """


class Backend:
    def __init__(self, backend, alive=False):
        self.host = backend["host"]
        self.port = backend["port"] if "port" in backend else 80
        self.alive = alive
        self.alive_lock = threading.Lock()

    def set_alive(self, alive):
        with self.alive_lock:
            self.alive = alive

    def is_alive(self):
        with self.alive_lock:
            return self.alive

    def __repr__(self):
        return f"(host: {self.host}, port: {self.port})"


class LoadBalancerHandler(BaseHTTPRequestHandler):

    """
    handler class for all incoming HTTP requests
    """

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super().__init__(*args, **kwargs)

    def log_request(self, code):
        pass

    def request_handler(self):

        content_len = self.headers["Content-Length"]
        self.body = None
        if content_len:
            self.body = self.rfile.read(int(content_len))

        backend = self.context.get_next_backend()

        if backend is None:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"no backends available")
            return

        conn = HTTPConnection(backend.host, backend.port)
        conn.request(self.command, self.path, headers=self.headers, body=self.body)

        resp = conn.getresponse()

        status = resp.status
        headers = resp.getheaders()
        body = resp.read()

        self.send_response(status)

        for header in headers:
            key, val = header
            self.send_header(key, val)
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        self.request_handler()

    def do_HEAD(self):
        self.request_handler()

    def do_POST(self):
        self.request_handler()

    def do_PUT(self):
        self.request_handler()

    def do_DELETE(self):
        self.request_handler()

    def do_PATCH(self):
        self.request_handler()


def process_config(config):
    return list(map(Backend, config["backends"]))
