import logging
import socket
import struct
import time
from dataclasses import dataclass
from enum import IntEnum

from trace.result_message import ResultMessage
from trace.tcp_packet import TcpIpPacket

icmp = socket.getprotobyname('icmp')
udp = socket.getprotobyname('udp')
logging.basicConfig(level=logging.DEBUG, filename="logging.log")


class IcmpType(IntEnum):
    PORT_UNREACHABLE_ERROR = 3


class IcmpCode(IntEnum):
    NET_UNREACHABLE = 0
    HOST_UNREACHABLE = 1
    PROTOCOL_UNREACHABLE = 2
    PORT_UNREACHABLE = 3
    FRAGMENTATION_NEEDED = 4


class TcpIpFlags(IntEnum):
    SYN_ACK = 18
    OTHER = 0


@dataclass
class Traceroute:
    host: str
    port: int = 33434
    max_hops: int = 30
    ttl: int = 1
    time_for_receive: int = 100
    number_of_request: int = 100
    ip_v6: bool = False
    packet_size: int = 40
    payload: str = ""
    interval_per_request: int = 5
    timeout_for_send: int = 5
    seq_number: int = 0
    icmp_type: IntEnum = None
    icmp_code: IntEnum = None
    tcp_flag: IntEnum = None
    final_address: str = None

    def get_data_for_record(self, address, send_time):
        recv_time = time.perf_counter()
        recv_host_address, recv_host_name = self.get_name_and_address(address)
        if recv_time < self.interval_per_request:
            time.sleep(self.interval_per_request - recv_time)
        return (
            f"{recv_host_name} ({recv_host_address})"
            f" {int((recv_time - send_time) * 1000)}ms ")

    def create_sockets(self) -> (socket, socket):
        recv_socket = socket.socket(
            socket.AF_INET if not self.ip_v6 else socket.AF_INET6,
            socket.SOCK_RAW,
            icmp)
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
        return trace_result.icmp_code == IcmpCode.PORT_UNREACHABLE.value and \
               trace_result.icmp_type == IcmpType.PORT_UNREACHABLE_ERROR.value

    def create_trace(self) -> ResultMessage:
        trace_results = []
        for request in range(0, self.number_of_request):
            recv_socket, send_socket = self.create_sockets()
            send_time = time.perf_counter()
            self.get_trace_result(recv_socket,
                                  send_socket,
                                  send_time,
                                  trace_results)
        return ResultMessage(ttl=self.ttl, icmp_type=self.icmp_type,
                             icmp_code=self.icmp_code, tcp_flag=self.tcp_flag,
                             results=trace_results)

    def get_trace_result(self, recv_socket, send_socket, send_time,
                         trace_results):
        try:
            self.send_data(send_socket)
        except socket.error as error:
            logging.warning(error)
        address = self.recv_data(recv_socket)
        trace_results.append(self.get_data_for_record(address, send_time))

    def get_name_and_address(self, address) -> (str, str):
        try:
            recv_host_name = socket.gethostbyaddr(str(address[0]))[0]
            recv_host_address = address[0]
        except socket.error:
            logging.debug(f"unknown name for address {address}")
            recv_host_name = ""
            recv_host_address = address[0]
        return recv_host_address, recv_host_name

    def send_data(self, send_socket):
        logging.info("UDP")
        send_socket.sendto(bytes(self.packet_size),
                           (self.host, self.port))

    def recv_data(self, recv_socket) -> str:
        try:
            packet, address = recv_socket.recvfrom(1024)
            self.icmp_type = packet[20]
            self.icmp_code = packet[21]

        except socket.timeout as error:
            logging.error(error)
            address = ("*",)
        return address


class TcpTraceroute(Traceroute):
    def create_sockets(self) -> socket:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_TCP)
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        send_socket.settimeout(self.timeout_for_send)
        recv_socket.settimeout(self.time_for_receive)
        return recv_socket, send_socket

    def get_trace_result(self, recv_socket, send_socket, send_time,
                         trace_results) -> (int, int):
        try:
            self.send_data(send_socket)
        except socket.error as error:
            logging.warning(error)
        address = self.recv_data_tcp(recv_socket, send_socket)
        trace_results.append(self.get_data_for_record(address, send_time))

    def recv_data_tcp(self, recv_socket, send_socket) -> str:
        try:
            packet, address = recv_socket.recvfrom(1024)
            self.icmp_type = packet[20]
            self.icmp_code = packet[21]
        except socket.timeout as error:
            logging.debug(error)
            try:
                address = self.get_tcp_status(send_socket)
            except socket.timeout:
                address = ("*",)
        return address

    def get_tcp_status(self, send_socket) -> str:
        tcp_data, address = send_socket.recvfrom(1024)
        tcp_header = struct.unpack("!HHLLBBHHH", tcp_data[20:40])
        try:
            self.tcp_flag = TcpIpFlags(tcp_header[5]).value
        except ValueError:
            logging.error(ValueError)
            self.tcp_flag = TcpIpFlags.OTHER
        return address

    def send_data(self, send_socket):
        try:
            source = self.get_source_ip()
            packet = TcpIpPacket(destination_port=80, host=self.host,
                                 ttl=self.ttl, source_port=self.port,
                                 source=source, seq=self.seq_number,
                                 payload=self.payload)
            logging.info("TCP")
            send_socket.sendto(packet.get_ip_tcp(), (self.host, self.port))
        except socket.error as error:
            logging.warning(error)

    @staticmethod
    def get_source_ip() -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 0))
            source = sock.getsockname()[0]
            return source

    def is_end(self, trace_result) -> bool:
        return trace_result.tcp_flag == TcpIpFlags.SYN_ACK.value
