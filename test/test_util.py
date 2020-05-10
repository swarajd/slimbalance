import io
from functools import partial
from unittest.mock import MagicMock, Mock, patch

from methods.util import LoadBalancerHandler


@patch("methods.util.HTTPConnection")
@patch("http.server.ThreadingHTTPServer")
def test_handler_no_backends(mock_http_server, mock_connection):
    """
    ensuring that the handler doesn't log anything upon request
    """

    mock_request = Mock()
    mock_request.makefile.return_value = io.BytesIO(b"GET /")

    context_mock = MagicMock()
    context_mock.get_next_backend.return_value = None

    HandlerClass = partial(LoadBalancerHandler, context_mock)

    handler = HandlerClass(mock_request, ("localhost", 8081), mock_http_server)
    handler.wfile = MagicMock()

    handler.do_GET()

    handler.wfile.write.assert_called_with(b"no backends available")
