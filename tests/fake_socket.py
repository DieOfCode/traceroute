class FakeSocket:
    def __init__(self, flag=0, *args):
        self.flag = flag

    def sendto(self, *args, **kwargs):
        return None

    def recvfrom(self, *args, **kwargs):
        return [0, 0, 0, 0, 0, 0, 18], ""

    def setsockopt(self, *args, **kwargs):
        return None

    def settimeout(self, *args, **kwargs):
        return None

    def connect(self, *args):
        return None

    def getsockname(self, *args):
        return ('192.168.1.1',)

    def close(self):
        return None
