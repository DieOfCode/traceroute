import logging
import random
import socket
import struct
import time
from dataclasses import dataclass
from enum import Enum

from trace.result_message import ResultMessage

icmp = socket.getprotobyname('icmp')
udp = socket.getprotobyname('udp')
logging.basicConfig(level=logging.DEBUG, filename="logging.log")


class IcmpType(Enum):
    PORT_UNREACHABLE_ERROR = 3


class IcmpCode(Enum):
    NET_UNREACHABLE = 0
    HOST_UNREACHABLE = 1
    PROTOCOL_UNREACHABLE = 2
    PORT_UNREACHABLE = 3
    FRAGMENTATION_NEEDED = 4


class TcpIpFlags(Enum):
    SYN_ACK = 18
    OTHER = 0


@dataclass
class Traceroute:
    host: str
    port: int = 33434
    max_hops: int = 30
    ttl: int = 1
    time_for_receive: int = 10
    number_of_request: int = 10
    tcp: bool = False
    packet_size: int = 40
    payload: str = ""
    interval_per_request: int = 5
    timeout_for_send: int = 5
    seq_number: int = 0
    icmp_type: int = None
    icmp_code: int = None
    tcp_flag: int = None
    final_address: str = None

    def create_sockets(self) -> socket:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        if self.tcp:
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                        socket.IPPROTO_TCP)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        else:
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                        socket.IPPROTO_UDP)
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)
        send_socket.settimeout(self.timeout_for_send)
        recv_socket.settimeout(self.time_for_receive)
        return recv_socket, send_socket

    def traceroute(self) -> str:
        while self.ttl <= self.max_hops:
            trace_result: ResultMessage = self.create_trace()
            yield trace_result
            self.ttl += 1
            self.seq_number += 1
            if self.is_end(trace_result):
                break

    def is_end(self, trace_result) -> bool:
        if self.tcp:
            return trace_result.tcp_flag == TcpIpFlags.SYN_ACK.value
        return trace_result.icmp_code == IcmpCode.PORT_UNREACHABLE.value and \
               trace_result.icmp_type == IcmpType.PORT_UNREACHABLE_ERROR.value

    def create_trace(self) -> ResultMessage:
        trace_results = []
        for request in range(0, self.number_of_request):
            recv_socket, send_socket = self.create_sockets()
            send_time = time.perf_counter()
            self.extract_data_for_result(recv_socket,
                                         send_socket,
                                         send_time,
                                         trace_results)
        return ResultMessage(ttl=self.ttl, icmp_type=self.icmp_type,
                             icmp_code=self.icmp_code, tcp_flag=self.tcp_flag,
                             results=trace_results)

    @staticmethod
    def get_source_ip() -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.168.1.1", 0))
            source = sock.getsockname()[0]
            return source

    def extract_data_for_result(self, recv_socket, send_socket, send_time,
                                trace_results) -> (int, int):
        try:
            if self.tcp:
                source = self.get_source_ip()
                packet = TCP_IP_PACK(destination_port=80, host=self.host,
                                     ttl=self.ttl, source_port=self.port,
                                     source=source, seq=self.seq_number,
                                     payload=self.payload)
                logging.info("TCP")
                send_socket.sendto(packet.get_ip_tcp(), (self.host, 80))
            else:
                logging.info("UDP")
                send_socket.sendto(bytes(self.packet_size),
                                   (self.host, self.port))
        except socket.error as error:
            logging.warning(error)
        try:
            packet, address = recv_socket.recvfrom(1024)
            self.icmp_type = packet[20]
            self.icmp_code = packet[21]

        except socket.error as error:
            logging.debug(error)
            address = ("*",)
            if self.tcp:
                try:
                    tcp_data, address = send_socket.recvfrom(1024)
                    tcp_header = struct.unpack("!HHLLBBHHH", tcp_data[20:40])
                    try:
                        print(TcpIpFlags(tcp_header[5]).value)
                        self.tcp_flag = TcpIpFlags(tcp_header[5]).value
                    except ValueError:
                        logging.error(ValueError)
                        self.tcp_flag = 0
                except socket.timeout:
                    address = ("*",)
        recv_time = time.perf_counter()
        try:
            recv_host_name = socket.gethostbyaddr(str(address[0]))[0]
            recv_host_address = address[0]
        except socket.error:
            logging.debug(f"unknown name for address {address}")
            recv_host_name = ""
            recv_host_address = address[0]
        if recv_time < self.interval_per_request:
            time.sleep(self.interval_per_request - recv_time)
        self.final_address = recv_host_address
        trace_results.append(
            f"{recv_host_name} ({recv_host_address})"
            f" {int((recv_time - send_time) * 1000)}ms ")


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
