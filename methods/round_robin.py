from http.server import BaseHTTPRequestHandler
from http.client import HTTPConnection
# from functools import partial

class RoundRobinContext:
    def __init__(self, config):
        self.hosts = config["hosts"]
        self.idx = 0
        self.host_len = len(self.hosts)

    def incr(self):
        self.idx = (self.idx + 1) % self.host_len
        print(self.idx)

# handler class for all incoming HTTP requests
class RoundRobinHandler(BaseHTTPRequestHandler):

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super().__init__(*args, **kwargs)

    def do_GET(self):

        print(self.client_address)
        print(self.path)

        self.context.incr()

        conn = HTTPConnection("www.example.com", 80)
        # print(conn)
        conn.request("GET", "/")
        resp = conn.getresponse()
        # print(resp.read())

        self.send_response(200)
        self.end_headers()