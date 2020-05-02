from http.server import BaseHTTPRequestHandler
from http.client import HTTPConnection
# from functools import partial
import threading

class RoundRobinContext:
    def __init__(self, config):
        self.hosts = config["hosts"]
        self.idx_lock = threading.Lock()
        self.idx = 0
        self.host_len = len(self.hosts)

    def get_host(self):
        host = self.hosts[self.idx]
        with self.idx_lock:
            self.idx = (self.idx + 1) % self.host_len
        return host

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

        host = self.context.get_host()

        conn = HTTPConnection(host)
        conn.request(
            self.command, 
            self.path,
            headers=self.headers,
            body=body
        )

        resp = conn.getresponse()

        self.send_response(resp.status)

        for header in resp.getheaders():
            key, val = header
            self.send_header(key, val)
        self.end_headers()

        self.wfile.write(resp.read())

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
        