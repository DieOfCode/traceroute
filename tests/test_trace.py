from collections import namedtuple
from typing import Dict, Callable
from unittest.mock import patch

import pytest

from tests.fake_socket import FakeSocket
from trace.result_message import ResultMessage
from trace.traceroute import Traceroute


@pytest.fixture
def set_up() -> Dict[int, namedtuple]:
    test_trace = Traceroute(max_hops=6, host="yandex.com", ttl=30,
                            time_for_receive=10, number_of_request=3,
                            interval_per_request=3, timeout_for_send=10,
                            seq_number=1, packet_size=40, port=33434,
                            payload="")
    result = namedtuple("Result", ["result_body", "type_icmp", "code_icmp"])
    all_results = {}
    for result_body, type_icmp, code_icmp in test_trace.traceroute():
        all_results[test_trace.ttl] = result(result_body, type_icmp, code_icmp)
    return all_results


@pytest.fixture
@patch("trace.traceroute.Traceroute.create_sockets",
       return_value=(FakeSocket(is_over=True, is_tcp=True),
                     FakeSocket(is_over=True, is_tcp=True)))
@patch("trace.traceroute.Traceroute.get_name_and_address",
       return_value=("", ""))
def trace_local(host, test) -> Dict[int, str]:
    test_trace = Traceroute(host="127.0.0.1")
    all_results = {}
    for result in test_trace.traceroute():
        all_results[test_trace.ttl] = result
    return all_results


@pytest.fixture
def set_up_for_test_end() -> Callable:
    def _is_end(end: bool):
        return ResultMessage(
            ['_gateway (192.168.0.1) 89ms ', '_gateway (192.168.0.1) 11ms ',
             '_gateway (192.168.0.1) 7ms '],
            ttl=2, icmp_code=3 if end else 0,
            icmp_type=3 if end else 0, tcp_flag=0)

    return _is_end


def test_icmp_code(set_up):
    for element in set_up.values():
        print(element)
        assert element.type_icmp == "TYPE:11"


def test_local(trace_local):
    assert list(trace_local.values())[0].icmp_type == 0


def test_is_end_false(set_up_for_test_end):
    with patch("trace.traceroute.Traceroute.create_trace") as test_recv:
        test_recv.return_value = set_up_for_test_end(False)
        a = Traceroute(host="127.0.0.1")
        assert a.is_end(a.create_trace()) is False


@patch("trace.traceroute.Traceroute.create_sockets",
       return_value=(FakeSocket(is_over=True, is_tcp=False),
                     FakeSocket(is_over=True, is_tcp=False)))
def test_is_end_true(test_sockets,
                     set_up_for_test_end):
    with patch("trace.traceroute.Traceroute.create_trace") as test_recv:
        test_recv.return_value = set_up_for_test_end(True)
        a = Traceroute(host="127.0.0.1")
        result = a.is_end(a.create_trace())
    assert result is True


def test_get_data_for_record():
    with patch("trace.traceroute.Traceroute.get_name_and_address") \
            as test_get_name_and_address:
        with patch("time.perf_counter") as test_time:
            test_time.return_value = 10
            test_get_name_and_address.return_value = ("127.0.0.1", "localhost")
            test_trace = Traceroute(host="127.0.0.1")
            assert test_trace.get_data_for_record(send_time=10,
                                                  address="127.0.0.1") \
                   == "localhost (127.0.0.1) 0ms "
