import socket
import time
from enum import Enum

from trace_util.result_message import ResultMessage

icmp = socket.getprotobyname('icmp')
udp = socket.getprotobyname('udp')


class IcmpType(Enum):
    PORT_UNREACHABLE_ERROR = 3


class IcmpCode(Enum):
    NET_UNREACHABLE = 0
    HOST_UNREACHABLE = 1
    PROTOCOL_UNREACHABLE = 2
    PORT_UNREACHABLE = 3
    FRAGMENTATION_NEEDED = 4


class Traceroute:
    def __init__(self, host, port, max_hops, first_ttl, time_per_request, number_of_request, ipv6) -> None:
        self.host = host
        self.port = port
        self.max_hops = int(max_hops)
        self.ttl = int(first_ttl)
        self.time_per_request = time_per_request
        self.number_of_request = number_of_request
        self._ipv6 = ipv6

    def create_sockets(self, ttl) -> socket:
        if not self._ipv6:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            return recv_socket, send_socket
        else:
            recv_socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW, proto=socket.IPPROTO_ICMPV6)
            send_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, udp)
            send_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl)
            return recv_socket, send_socket

    def traceroute(self) -> str:
        while self.ttl <= self.max_hops:
            trace_result: ResultMessage = self.create_trace(self.ttl)
            yield trace_result
            self.ttl += 1
            if trace_result.icmp_code == IcmpCode.PORT_UNREACHABLE \
                    and trace_result.icmp_type == IcmpType.PORT_UNREACHABLE_ERROR:
                break

    def create_trace(self, ttl) -> ResultMessage:
        icmp_type = None
        icmp_code = None
        trace_results = []

        for request in range(0, self.number_of_request):
            time.sleep(self.time_per_request)
            recv_socket, send_socket = self.create_sockets(ttl)
            recv_socket.settimeout(10)
            send_time = time.perf_counter()
            icmp_code, icmp_type = self.extract_data_for_result(recv_socket, send_socket,
                                                                send_time, trace_results)

        return ResultMessage(ttl=ttl, icmp_type=icmp_type, icmp_code=icmp_code, results=trace_results)

    def extract_data_for_result(self, recv_socket, send_socket, send_time, trace_results) -> (int, int):
        try:
            send_socket.sendto(b"", (self.host, self.port))
        except socket.error as error:
            print(error)
        try:
            packet, address = recv_socket.recvfrom(1024)
            icmp_type = packet[20]
            icmp_code = packet[21]
        except socket.error:
            address = ("*",)
            icmp_type = None
            icmp_code = None
        recv_time = time.perf_counter()
        try:
            recv_host_name = socket.gethostbyaddr(str(address[0]))[0]
            recv_host_address = address[0]
        except socket.error:
            recv_host_name = ""
            recv_host_address = address[0]
        trace_results.append(f"{recv_host_name} ({recv_host_address}) {int((recv_time - send_time) * 1000)}ms ")
        return icmp_code, icmp_type
