from mock import patch
import pytest
from collections import namedtuple

from trace_util.traceroute import Traceroute

@pytest.fixture
def set_up():
    test_trace = Traceroute(first_ttl=3, max_hops=6, host="yandex.com")
    result = namedtuple("Result", ["result_body", "type_icmp", "code_icmp"])
    all_results = {}
    for result_body, type_icmp, code_icmp in test_trace.traceroute():
        all_results[test_trace.ttl] = result(result_body, type_icmp, code_icmp)
    return all_results


@pytest.fixture
def trace_local():
    test_trace = Traceroute(host="127.0.0.1")
    result = namedtuple("Result", ["result_body", "type_icmp", "code_icmp"])
    all_results = {}
    for result_body, type_icmp, code_icmp in test_trace.traceroute():
        all_results[test_trace.ttl] = result(result_body, type_icmp, code_icmp)
    return all_results


def test_hops(set_up):
    assert list(set_up.keys())[0] == 3
    assert list(set_up.keys())[-1] == 6


def test_icmp_code(set_up):
    for element in set_up.values():
        assert element.type_icmp == "TYPE:11"


def test_local(trace_local):
    assert list(trace_local.values())[0].type_icmp == "TYPE:3"


def test_create_trace():
    with patch("socket.socket.recvfrom") as test_recv:
        test_recv.return_value = (b'E\xc0\x008\xb5\xac\x00\x00@\x01\xc6V\x7f\x00\x00\x01\x7f\x00\x00\x01\x03\x03\xe1N'
                                  b'\x00\x00\x00\x00E\x00\x00\x1c\xf7\x04@\x00\x01\x11\x84\xca\x7f\x00\x00\x01\x7f'
                                  b'\x00\x00\x01\x9a\xef\x82\x9a\x00\x08\xfe\x1b'[0:], ('127.0.0.1', 0))

        a = Traceroute(host="127.0.0.1")
        assert a.create_trace(1) == (
            3, 3, '1:localhost (127.0.0.1) 0ms localhost (127.0.0.1) 0ms localhost (127.0.0.1) 0ms ')


