import io
from functools import partial
from unittest.mock import MagicMock, Mock, patch, call

from methods.util import LoadBalancerHandler, Backend


@patch("http.server.ThreadingHTTPServer")
def test_handler_no_backends(mock_http_server):
    """
    ensuring that the handler doesn't log anything upon request
    """

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(b"GET / HTTP/1.1")

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = None

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, ("localhost", 8080), mock_http_server)
    handler.wfile = MagicMock()

    handler.do_GET()

    handler.wfile.write.assert_called_with(b"no backends available")

@patch("methods.util.HTTPConnection")
@patch("http.server.ThreadingHTTPServer")
def test_handler_return_data(mock_http_server, mock_connection):
    """
    ensuring that the handler returns the request data from the backend
    appropriately
    """

    class DummyResponse:
        def __init__(self, status, headers, content):
            self.status = status
            self.headers = headers
            self.content = content
        
        def getheaders(self):
            return self.headers
        
        def read(self):
            return self.content

    content = "a=1&b=2"
    request_str = f"POST / HTTP/1.1\nContent-Length: {len(content)}\nContent-Type: application/x-www-form-urlencoded\n\n{content}"
    request_bytes = bytes(request_str, 'utf-8')

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(request_bytes)

    STATUS = 200
    HEADERS = [('c', 'd'), ('e', 'f')]
    CONTENT = bytes(content, "utf-8")

    conn = MagicMock()
    conn.getresponse.return_value = DummyResponse(STATUS, HEADERS, CONTENT)

    mock_connection.return_value = conn

    REQUEST_HOST = 'localhost'
    REQUEST_PORT = 8080

    BACKEND_HOST = 'localhost'
    BACKEND_PORT = 8081

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = Backend({
        'host': BACKEND_HOST,
        'port': BACKEND_PORT
    }, alive=True)

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, ("localhost", 8080), mock_http_server)
    handler.wfile = MagicMock()
    handler.rfile = MagicMock()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()

    handler.rfile.read.return_value = content

    handler.do_POST()

    handler.send_response.assert_called_with(STATUS)

    calls = list(map(lambda h: call(h[0], h[1]), HEADERS))
    handler.send_header.assert_has_calls(calls)

@patch("methods.util.HTTPConnection")
@patch("http.server.ThreadingHTTPServer")
def test_handler_request_data(mock_http_server, mock_connection):
    """
    ensuring that the handler gets the appropriate request data
    """

    class DummyResponse:
        def __init__(self, status, headers, content):
            self.status = status
            self.headers = headers
            self.content = content
        
        def getheaders(self):
            return self.headers
        
        def read(self):
            return self.content

    content = "a=1&b=2"
    request_str = f"POST / HTTP/1.1\nContent-Length: {len(content)}\nContent-Type: application/x-www-form-urlencoded\n\n{content}"
    request_bytes = bytes(request_str, 'utf-8')

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(request_bytes)

    STATUS = 200
    HEADERS = [('c', 'd'), ('e', 'f')]
    CONTENT = bytes(content, "utf-8")

    conn = MagicMock()
    conn.getresponse.return_value = DummyResponse(STATUS, HEADERS, CONTENT)

    mock_connection.return_value = conn

    REQUEST_HOST = 'localhost'
    REQUEST_PORT = 8080

    BACKEND_HOST = 'localhost'
    BACKEND_PORT = 8081

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = Backend({
        'host': BACKEND_HOST,
        'port': BACKEND_PORT
    }, alive=True)

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, (REQUEST_HOST, REQUEST_PORT), mock_http_server)
    handler.wfile = MagicMock()
    handler.rfile = MagicMock()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()

    # TODO: fix this so this value comes from the actual request
    handler.rfile.read.return_value = content

    handler.do_POST()

    handler.rfile.read.assert_called_with(len(content))