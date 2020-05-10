import threading


class Backend:
    def __init__(self, backend, alive=False):
        self.host = backend["host"]
        self.port = backend["port"] if "port" in backend else 80
        self.alive = alive
        self.alive_lock = threading.Lock()

    def set_alive(self, alive):
        with self.alive_lock:
            self.alive = alive

    def is_alive(self):
        with self.alive_lock:
            return self.alive

    def __repr__(self):
        return f"(host: {self.host}, port: {self.port})"
