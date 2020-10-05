import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock1 = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
sock.sendto(b'', (socket.gethostbyname('google.ru'), 33434))
sock1.setsockopt(socket.SOL_IP, socket.IP_TTL, 1)
data, addr = sock1.recvfrom(1024)
print(addr[0])