import socket
import struct
from dataclasses import dataclass


@dataclass
class FakeSocket:
    is_tcp: bool
    is_over: bool
    q: bool = False
    proto = 6

    def sendto(self, *args, **kwargs):
        return None

    def recvfrom(self, *args, **kwargs):
        return self.get_pack()

    def setsockopt(self, *args, **kwargs):
        return None

    def settimeout(self, *args, **kwargs):
        return None

    def connect(self, *args):
        return None

    def getsockname(self, *args):
        return '192.168.1.1',

    def close(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def get_pack(self):
        if self.is_tcp:
            eth_protocol = 8
            eth_data = struct.pack('!12xH', socket.htons(eth_protocol))
            ttl = 255
            ip_protocol = 6
            source_ip = '192.168.1.1'
            destination_ip = '192.168.1.152'
            ip_data = struct.pack('!8xBB2x4s4s', ttl, ip_protocol,
                                  socket.inet_aton(source_ip),
                                  socket.inet_aton(destination_ip))
            if self.is_over:
                tcp_flags = 18
            else:
                tcp_flags = 0
            tcp_data = struct.pack('!HHLLBBHHH', 0, 0, 0, 0, 0,
                                   tcp_flags, 0, 0, 0)
            return eth_data + ip_data + tcp_data, source_ip
        eth_protocol = 8
        eth_data = struct.pack('!12xH', socket.htons(eth_protocol))
        ttl = 255
        ip_protocol = 1
        source_ip = '192.168.1.1'
        destination_ip = '192.168.1.152'
        ip_data = struct.pack('!8xBB2x4s4s', ttl, ip_protocol,
                              socket.inet_aton(source_ip),
                              socket.inet_aton(destination_ip))
        if self.is_over:
            icmp_data = struct.pack('!BB', 3, 3)
        else:
            icmp_data = struct.pack('!BB', 11, 3)
        return eth_data + ip_data + icmp_data, source_ip
