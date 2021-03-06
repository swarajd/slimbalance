import hashlib

from .context import Context


class IPHashContext(Context):
    def __init__(self, backends):
        self.backends = backends
        self.backend_len = len(self.backends)

    def get_next_backend(self, context):
        cur_hash = int(
            hashlib.sha1(context["address"][0].encode("ascii")).hexdigest(), 16
        )
        next_idx = cur_hash % self.backend_len
        print(next_idx)
        max_idx = self.backend_len + next_idx
        i = next_idx
        while i < max_idx:
            idx = i % self.backend_len
            if self.backends[idx].is_alive():
                return self.backends[idx]
            i += 1

        return None

    def cleanup(self, backend):
        pass
