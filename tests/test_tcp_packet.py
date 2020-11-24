from unittest.mock import patch

from pytest import fixture

from trace.tcp_packet import TcpIpPacket


@fixture
def test_tcp_packet():
    return TcpIpPacket(source="127.0.0.1", ttl=1, source_port=80,
                       destination_port=80, host="google.com")


def test_get_tcp_packet(test_tcp_packet):
    with patch("random.randint") as test_random:
        test_random.return_value = 0
        test_tcp_packet.source = b""
        test_tcp_packet.host = b""
        print(test_tcp_packet.get_ip_tcp())
        assert test_tcp_packet.get_ip_tcp() == b'E\x00\x00(' \
                                               b'\x00\x00\x00\x00\x01\x06' \
                                               b'\x00\n\x00\x00\x00\x00\x00' \
                                               b'\x00\x00\x00\x00P\x00P\x00' \
                                               b'\x00\x00\x00\x00\x00\x00' \
                                               b'\x00P\x02\xd0\x16\xdf,' \
                                               b'\x00\x00'


def test_checksum(test_tcp_packet):
    assert test_tcp_packet.checksum(b"123123") == 26985
