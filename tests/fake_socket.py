import socket
from dataclasses import dataclass


@dataclass
class FakeSocket:
    raise_error: bool

    def sendto(self, *args, **kwargs):
        return None

    def recvfrom(self, *args, **kwargs):
        if not self.raise_error:
            return [0, 0, 0, 0, 0, 0, 18], ""
        raise socket.timeout

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
