# import queue
# import threading
# from collections import defaultdict

# from methods.round_robin import RoundRobinContext
import socket
from unittest.mock import MagicMock, patch

from healthcheck import healthcheck


@patch("healthcheck.socket.socket")
def test_healthcheck_ok(socket_mock):
    """
    testing to see if the health check method
    returns True if the socket is able to be
    connected to
    """

    HOST = "testhost"
    PORT = 1234
    result = healthcheck(HOST, PORT)
    assert result


@patch("healthcheck.socket.socket")
def test_healthcheck_timeout(socket_mock):
    """
    testing to see if the health check method
    returns False if the socket times out
    """

    socket_instance = MagicMock()
    socket_instance.connect.side_effect = socket.timeout

    socket_mock.return_value = socket_instance

    HOST = "testhost"
    PORT = 1234
    result = healthcheck(HOST, PORT)
    assert not result


@patch("healthcheck.socket.socket")
def test_healthcheck_no_response(socket_mock):
    """
    testing to see if the health check method
    returns False if the socket times out
    """

    socket_instance = MagicMock()
    socket_instance.connect.side_effect = OSError

    socket_mock.return_value = socket_instance

    HOST = "testhost"
    PORT = 1234
    result = healthcheck(HOST, PORT)
    assert not result
