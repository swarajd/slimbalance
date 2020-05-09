import threading


class RoundRobinContext:
    def __init__(self, backends):
        self.backends = backends
        self.idx_lock = threading.Lock()
        self.idx = 0
        self.backend_len = len(self.backends)

    def next_index(self):
        with self.idx_lock:
            self.idx = (self.idx + 1) % self.backend_len
            return self.idx

    def get_next_backend(self):
        next_idx = self.next_index()
        max_idx = self.backend_len + next_idx
        i = next_idx
        while i < max_idx:
            idx = i % self.backend_len
            if self.backends[idx].is_alive():
                if i != next_idx:
                    with self.idx_lock:
                        self.idx = idx
                return self.backends[idx]
            i += 1

        return None
