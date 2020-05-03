import threading

class Backend:
    def __init__(self, backend):
        self.host = backend["host"]
        self.port = backend["port"] if "port" in backend else 80
        self.alive = False
        self.alive_lock = threading.Lock()

    def set_alive(self, alive):
        with self.alive_lock:
            self.alive = alive

    def is_alive(self):
        alive = False
        with self.alive_lock:
            alive = self.alive
        return alive

    def __repr__(self):
        return f"(url: {self.url})"

def process_config(config):
    return list(map(Backend, config["backends"]))