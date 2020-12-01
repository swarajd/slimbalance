from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler


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

        context = {"address": self.client_address, "headers": self.headers}

        backend = self.context.get_next_backend(context)

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
