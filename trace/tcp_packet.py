import random
import socket
import struct


class TCP_IP_PACK:
    def __init__(self, source, host, ttl, source_port, destination_port,
                 seq=0, payload=''):
        self.source: bytes = socket.inet_aton(source)
        self.host: bytes = socket.inet_aton(socket.gethostbyname(host))
        self.source_port: int = source_port
        self.destination_port: int = destination_port
        self.ttl: int = ttl
        self.seq: int = seq
        try:
            self.payload = bytes(payload, encoding='utf-8')
        except TypeError:
            self.payload = bytes(payload)

    def checksum(self, msg: bytes) -> int:
        check = 0
        for i in range(0, len(msg), 2):
            temp = (msg[i] << 8) + (msg[i + 1])
            check = check + temp
            check = (check >> 16) + (check & 0xffff)
        check = ~check & 0xffff
        return check

    def get_tcp_pack(self) -> bytes:
        source_port = self.source_port
        destination_port = self.destination_port
        window = socket.htons(5840)
        check = 0
        urg_ptr = 0
        offset_res = (5 << 4) + 0
        tcp_flags = 0 + (1 << 1) + (0 << 2) + (0 << 3) + (0 << 4) + (
                0 << 5)
        tcp_header = struct.pack(f'!HHLLBBHHH{len(self.payload)}s',
                                 source_port,
                                 destination_port,
                                 self.seq,
                                 0,
                                 offset_res,
                                 tcp_flags,
                                 window,
                                 check,
                                 urg_ptr,
                                 self.payload)
        placeholder = 0
        tcp_length = len(tcp_header)
        psh = struct.pack('!4s4sBBH', self.source, self.host, placeholder,
                          socket.IPPROTO_TCP, tcp_length)
        psh = psh + tcp_header
        tcp_checksum = self.checksum(psh)
        tcp_header = struct.pack(f'!HHLLBBHHH{len(self.payload)}s',
                                 source_port,
                                 destination_port,
                                 self.seq,
                                 0,
                                 offset_res,
                                 tcp_flags,
                                 window,
                                 tcp_checksum,
                                 urg_ptr,
                                 self.payload)
        return tcp_header

    def get_ip_pack(self) -> bytes:
        ihl = 5
        version = 4
        tos = 0
        tot_len = 40
        id = random.randint(20000, 60000)
        fragment_offset = 0
        protocol = socket.IPPROTO_TCP
        check = 10
        ihl_version = (version << 4) + ihl
        ip_header = struct.pack('!BBHHHBBH4s4s',
                                ihl_version,
                                tos,
                                tot_len,
                                id,
                                fragment_offset,
                                self.ttl,
                                protocol,
                                check,
                                self.source,
                                self.host)
        return ip_header

    def get_ip_tcp(self) -> bytes:
        return self.get_ip_pack() + self.get_tcp_pack()
