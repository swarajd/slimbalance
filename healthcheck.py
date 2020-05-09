import socket
import time


def healthcheck(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RD)
        return True
    except socket.timeout:
        return False
    except OSError:
        return False


def health_checks(backends):
    while True:
        for backend in backends:
            alive = healthcheck(backend.host, backend.port)
            backend.set_alive(alive)
        time.sleep(20)