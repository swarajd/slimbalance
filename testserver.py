from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class TestHandler(BaseHTTPRequestHandler):
    def log_request(self, code):
        pass

    def request_handler(self):
        print(self.client_address)
        print(self.path)
        print(self.command)
        print(self.requestline)
        print(self.request_version)
        print(self.headers)

        content_len = self.headers["Content-Length"]
        body = None
        if content_len:
            body = self.rfile.read(int(content_len))
            print(body)

        self.send_response(200)
        self.end_headers()

        self.wfile.write(b"ok")

    def do_GET(self):
        self.request_handler()

    def do_POST(self):
        self.request_handler()


# some sane defaults
HOSTNAME = "localhost"
PORT = 8081

if __name__ == "__main__":

    test_server = ThreadingHTTPServer((HOSTNAME, PORT), TestHandler)
    print(f"Server started: http://{HOSTNAME}:{PORT}")

    try:
        test_server.serve_forever()
    except KeyboardInterrupt:
        pass

    test_server.server_close()
    print("Server stopped.")
