from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPConnection
import json

from methods import RoundRobin

# some sane defaults
HOSTNAME = "localhost"
PORT     = 8080

# handler class for all incoming HTTP requests
class LoadBalancer(BaseHTTPRequestHandler):
    def do_GET(self):
        global round_robin

        print(self.client_address)
        print(self.path)

        round_robin.incr()

        conn = HTTPConnection("www.example.com", 80)
        # print(conn)
        conn.request("GET", "/")
        resp = conn.getresponse()
        # print(resp.read())

        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # load config
    with open("config.json", "r") as conf:
        config = json.loads(conf.read())

    # reading hosts
    host_index = 0
    hosts = config["hosts"]

    round_robin = RoundRobin(hosts)

    load_balancer = ThreadingHTTPServer((HOSTNAME, PORT), LoadBalancer)
    print(f"Server started: http://{HOSTNAME}:{PORT}")

    try:
        load_balancer.serve_forever()
    except KeyboardInterrupt:
        pass

    load_balancer.server_close()
    print("Server stopped.")