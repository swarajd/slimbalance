class RoundRobin:
    def __init__(self, hosts):
        self.hosts = hosts
        self.idx = 0
        self.host_len = len(hosts)

    def incr(self):
        self.idx = (self.idx + 1) % self.host_len
        print(self.idx)

    