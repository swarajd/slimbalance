from http.server import BaseHTTPRequestHandler
from http.client import HTTPConnection

from config import HOSTNAME, PORT

import threading

class RoundRobinContext:
    def __init__(self, backends):
        self.backends = backends
        self.idx_lock = threading.Lock()
        self.idx = 0
        self.backend_len = len(self.backends)

    def next_index(self):
        n_idx = -1
        with self.idx_lock:
            self.idx = (self.idx + 1) % self.backend_len
            n_idx = self.idx
        return n_idx

    def get_next_backend(self):
        next_idx = self.next_index()
        l = self.backend_len + next_idx
        i = next_idx
        while i < l:
            idx = i % self.backend_len
            if self.backends[idx].is_alive():
                if i != next_idx:
                    with self.idx_lock():
                        self.idx = idx
                return self.backends[idx]
            i += 1
        
        return None

# handler class for all incoming HTTP requests
class RoundRobinHandler(BaseHTTPRequestHandler):

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super().__init__(*args, **kwargs)

    def log_request(self, code): 
        pass

    def request_handler(self):

        content_len = self.headers['Content-Length']
        body=None
        if content_len: 
            body = self.rfile.read(int(content_len))

        backend = self.context.get_next_backend()

        if backend is None:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'no backends available')
            return

        # Check if the host matches the load balancer IP and replace accordingly
        if "Host" in self.headers and self.headers["Host"] == f"{HOSTNAME}:{PORT}":
            del self.headers["Host"]
            self.headers["Host"] = f"{backend.host}:{backend.port}"

        conn = HTTPConnection(backend.host, backend.port)
        conn.request(
            self.command, 
            self.path,
            headers=self.headers,
            body=body
        )

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
        