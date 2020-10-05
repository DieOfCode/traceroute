import socket
import time

icmp = socket.getprotobyname('icmp')
udp = socket.getprotobyname('udp')


class Traceroute():
    def __init__(self, host, port=33434, max_hops=30, first_ttl=1) -> None:
        self.host = host
        self.port = port
        self.max_hops = int(max_hops)
        self.ttl = int(first_ttl)

    def create_sockets(self, ttl) -> socket:
        """
        Sets up sockets necessary for the trace_util.  We need a receiving
        socket and a sending socket.
        """
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        return recv_socket, send_socket

    def traceroute(self):
        while self.ttl <= self.max_hops:
            icmp_type, icmp_code, trace_result = self.create_trace(self.ttl)

            yield trace_result, f"TYPE:{icmp_type}", f"CODE:{icmp_code}"
            self.ttl += 1
            if icmp_code == 3 and icmp_type == 3:
                break

    def create_trace(self, ttl):
        trace_result = f"{ttl}:"
        for request in range(0, 3):
            recv_socket, send_socket = self.create_sockets(ttl)
            recv_socket.settimeout(10)
            send_time = time.time()
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
            recv_time = time.time()
            try:

                recv_host_name = socket.gethostbyaddr(str(address[0]))[0]
                recv_host_address = address[0]
            except socket.error:
                recv_host_name = ""
                recv_host_address = address[0]
            trace_result += f"{recv_host_name} ({recv_host_address}) {int((recv_time - send_time) * 1000)}ms "

        return icmp_type, icmp_code, trace_result
