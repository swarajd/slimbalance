import io
from functools import partial
from unittest.mock import MagicMock, Mock, call, patch

from handler import LoadBalancerHandler
from methods.util import Backend


class DummyResponse:
    def __init__(self, status, headers, content):
        self.status = status
        self.headers = headers
        self.content = content

    def getheaders(self):
        return self.headers

    def read(self):
        return self.content


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


@patch("handler.HTTPConnection")
@patch("http.server.ThreadingHTTPServer")
def test_handler_return_data(mock_http_server, mock_connection):
    """
    ensuring that the handler returns the request data from the backend
    appropriately
    """

    REQUEST_CONTENT = "a=1&b=2"
    REQUEST_STR = f"POST / HTTP/1.1\nContent-Length: {len(REQUEST_CONTENT)}\nContent-Type: application/x-www-form-urlencoded\n\n{REQUEST_CONTENT}"
    REQUEST_BYTES = bytes(REQUEST_STR, "utf-8")

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(REQUEST_BYTES)

    RESPONSE_STATUS = 200
    RESPONSE_HEADERS = [("c", "d"), ("e", "f")]
    RESPONSE_CONTENT = bytes("asdf", "utf-8")

    conn = MagicMock()
    conn.getresponse.return_value = DummyResponse(
        RESPONSE_STATUS, RESPONSE_HEADERS, RESPONSE_CONTENT
    )

    mock_connection.return_value = conn

    REQUEST_HOST = "localhost"
    REQUEST_PORT = 8080

    BACKEND_HOST = "localhost"
    BACKEND_PORT = 8081

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = Backend(
        {"host": BACKEND_HOST, "port": BACKEND_PORT}, alive=True
    )

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, (REQUEST_HOST, REQUEST_PORT), mock_http_server)
    handler.wfile = MagicMock()
    handler.rfile = MagicMock()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()

    handler.rfile.read.return_value = RESPONSE_CONTENT

    handler.do_POST()

    handler.send_response.assert_called_with(RESPONSE_STATUS)

    calls = list(map(lambda h: call(h[0], h[1]), RESPONSE_HEADERS))
    handler.send_header.assert_has_calls(calls)

    handler.wfile.write.assert_called_with(RESPONSE_CONTENT)


@patch("handler.HTTPConnection")
@patch("http.server.ThreadingHTTPServer")
def test_handler_request_data(mock_http_server, mock_connection):
    """
    ensuring that the handler gets the appropriate request data
    """

    REQUEST_COMMAND = "POST"
    REQUEST_PATH = "/"
    REQUEST_CONTENT = "a=1&b=2"
    REQUEST_CONTENT_BYTES = bytes(REQUEST_CONTENT, "utf-8")
    REQUEST_HEADERS = {
        "Content-Length": str(len(REQUEST_CONTENT)),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    REQUEST_HEADER_STR = "\n".join(
        [f"{key}: {val}" for key, val in REQUEST_HEADERS.items()]
    )

    request_str = f"{REQUEST_COMMAND} {REQUEST_PATH} HTTP/1.1\n{REQUEST_HEADER_STR}\n\n{REQUEST_CONTENT}"
    request_bytes = bytes(request_str, "utf-8")

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(request_bytes)

    RESPONSE_STATUS = 200
    RESPONSE_HEADERS = [("c", "d"), ("e", "f")]
    RESPONSE_CONTENT = b"dummy data"

    conn = MagicMock()
    conn.getresponse.return_value = DummyResponse(
        RESPONSE_STATUS, RESPONSE_HEADERS, RESPONSE_CONTENT
    )

    mock_connection.return_value = conn

    REQUEST_HOST = "localhost"
    REQUEST_PORT = 8080

    BACKEND_HOST = "localhost"
    BACKEND_PORT = 8081

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = Backend(
        {"host": BACKEND_HOST, "port": BACKEND_PORT}, alive=True
    )

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, (REQUEST_HOST, REQUEST_PORT), mock_http_server)

    assert handler.command == REQUEST_COMMAND
    assert handler.path == REQUEST_PATH
    for header in handler.headers:
        assert REQUEST_HEADERS[header] == handler.headers[header]
    assert handler.body == REQUEST_CONTENT_BYTES


# TODO: abstract out the setup process somehow
@patch("handler.HTTPConnection")
@patch("http.server.ThreadingHTTPServer")
def test_handler_put(mock_http_server, mock_connection):
    """
    testing PUT method
    """

    # set up request
    REQUEST_COMMAND = "PUT"
    REQUEST_PATH = "/"
    REQUEST_CONTENT = "a=1&b=2"
    REQUEST_CONTENT_BYTES = bytes(REQUEST_CONTENT, "utf-8")
    REQUEST_HEADERS = {
        "Content-Length": str(len(REQUEST_CONTENT)),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    REQUEST_HEADER_STR = "\n".join(
        [f"{key}: {val}" for key, val in REQUEST_HEADERS.items()]
    )

    request_str = f"{REQUEST_COMMAND} {REQUEST_PATH} HTTP/1.1\n{REQUEST_HEADER_STR}\n\n{REQUEST_CONTENT}"
    request_bytes = bytes(request_str, "utf-8")

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(request_bytes)

    # set up response
    RESPONSE_STATUS = 200
    RESPONSE_HEADERS = [("c", "d"), ("e", "f")]
    RESPONSE_CONTENT = b"dummy data"

    conn = MagicMock()
    conn.getresponse.return_value = DummyResponse(
        RESPONSE_STATUS, RESPONSE_HEADERS, RESPONSE_CONTENT
    )

    mock_connection.return_value = conn

    # set up backend
    BACKEND_HOST = "localhost"
    BACKEND_PORT = 8081

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = Backend(
        {"host": BACKEND_HOST, "port": BACKEND_PORT}, alive=True
    )

    # set up handler
    REQUEST_HOST = "localhost"
    REQUEST_PORT = 8080

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, (REQUEST_HOST, REQUEST_PORT), mock_http_server)

    # make assertions
    assert handler.command == REQUEST_COMMAND
    assert handler.path == REQUEST_PATH
    for header in handler.headers:
        assert REQUEST_HEADERS[header] == handler.headers[header]
    assert handler.body == REQUEST_CONTENT_BYTES
