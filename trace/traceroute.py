import logging
import socket
import struct
import time
from dataclasses import dataclass
from enum import Enum

from trace.result_message import ResultMessage
from trace.tcp_packet import TCP_IP_PACK

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
