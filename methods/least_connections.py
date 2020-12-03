import threading
from collections import defaultdict

from .context import Context


class LeastConnectionsContext(Context):
    def __init__(self, backends):
        self.backends = backends
        self.backend_len = len(self.backends)
        self.connection_dict = defaultdict(int)
        self.connection_dict_lock = threading.Lock()

        self.backend_dict = {[backend.id]: backend for backend in backends}

    def get_next_backend(self, context):
        while True:
            # note: yes I could use a reader/writer lock for the connection dict,
            # but just for the PoC I'm using a regular lock
            with self.connection_dict_lock:
                if len(self.connection_dict) == 0:
                    return None

                # grab the backend with the least connections
                cur_backend_id = min(
                    self.connection_dict.keys(), key=(lambda k: self.connection_dict[k])
                )

                cur_backend = self.backend_dict[cur_backend_id]

                # return if alive, remove from the dict if not
                if not cur_backend.is_alive():
                    self.connection_dict.pop(cur_backend.id)
                else:
                    return cur_backend

    def cleanup(self, backend):
        with self.connection_dict_lock:
            self.connection_dict[backend.id] = min(
                0, self.connection_dict[backend.id] - 1
            )
