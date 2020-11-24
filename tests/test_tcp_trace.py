from unittest.mock import patch

from pytest import fixture

from tests.fake_socket import FakeSocket
from trace.result_message import ResultMessage
from trace.traceroute import TcpTraceroute


@fixture()
def tcp_traceroute():
    return TcpTraceroute("127.0.0.1")


@patch("struct.unpack", return_value=[0, 0, 0, 0, 0, 18])
def test_get_tcp_status(test_unpack):
    test_tcp_trace = TcpTraceroute("127.0.0.1")
    print(test_tcp_trace.get_tcp_status(FakeSocket()))
    assert test_tcp_trace.tcp_flag == 18


def test_tcp_is_end(tcp_traceroute):
    assert tcp_traceroute.is_end(
        ResultMessage(["", "", ""], 1, 0, 0, 18)) is True


def test_create_tcp_socket(tcp_traceroute):
    assert tcp_traceroute.create_sockets()[1].proto == 6


def test_get_trace_result(tcp_traceroute):
    with patch("trace.traceroute.TcpTraceroute.recv_data_tcp") as test_recv:
        test_recv.return_value = "127.0.0.1"
        test_result = []
        tcp_traceroute.get_trace_result(FakeSocket(), FakeSocket(), 10,
                                        test_result)
        assert len(test_result) == 1
