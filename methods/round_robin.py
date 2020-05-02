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
        print(self.client_address)
        print(self.path)
        print(self.command)
        print(self.requestline)
        print(self.request_version)
        print(self.rfile.read(
            int(self.headers['Content-Length'])
        ))

        # host = self.context.get_host()

        self.send_response(200)
        self.end_headers()

        # conn = HTTPConnection(host)
        # print(conn)
        # conn.request("GET", self.path)
        # resp = conn.getresponse()
        # self.wfile.write(resp.read())
        # self.wfile.close()

    def do_POST(self):
        self.request_handler()
        