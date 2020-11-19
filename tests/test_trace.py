from typing import Dict

import function
from mock import patch
import pytest
from collections import namedtuple

from trace.result_message import ResultMessage
from trace.traceroute import Traceroute


@pytest.fixture
def set_up() -> Dict[int, namedtuple]:
    test_trace = Traceroute(max_hops=6, host="yandex.com", ttl=30,
                            time_for_receive=10, number_of_request=3,
                            interval_per_request=3, timeout_for_send=10,
                            seq_number=1, packet_size=40, port=33434,
                            payload="", tcp=False)
    result = namedtuple("Result", ["result_body", "type_icmp", "code_icmp"])
    all_results = {}
    for result_body, type_icmp, code_icmp in test_trace.traceroute():
        all_results[test_trace.ttl] = result(result_body, type_icmp, code_icmp)
    return all_results


@pytest.fixture
def trace_local() -> Dict[int, str]:
    test_trace = Traceroute(host="127.0.0.1")
    all_results = {}
    for result in test_trace.traceroute():
        all_results[test_trace.ttl] = result
    return all_results


@pytest.fixture
def set_up_for_test_end() -> function:
    def _is_end(end: bool):
        return ResultMessage(
            ['_gateway (192.168.0.1) 89ms ', '_gateway (192.168.0.1) 11ms ',
             '_gateway (192.168.0.1) 7ms '],
            ttl=2, icmp_code=3 if end else 0,
            icmp_type=3 if end else 0, tcp_flag=0)

    return _is_end


def test_icmp_code(set_up):
    for element in set_up.values():
        assert element.type_icmp == "TYPE:11"


def test_local(trace_local):
    assert list(trace_local.values())[0].icmp_type == 3


def test_is_end_true(set_up_for_test_end):
    with patch("trace.traceroute.Traceroute.create_trace") as test_recv:
        test_recv.return_value = set_up_for_test_end(True)
        a = Traceroute(host="127.0.0.1")
        assert a.is_end(a.create_trace()) is True


def test_is_end_false(set_up_for_test_end):
    with patch("trace.traceroute.Traceroute.create_trace") as test_recv:
        test_recv.return_value = set_up_for_test_end(False)
        a = Traceroute(host="127.0.0.1")

        assert a.is_end(a.create_trace()) is False


def test_result():
    result = []
    a = Traceroute(host="google.com", max_hops=2)
    for i in a.traceroute():
        result.append(i)
    assert len(result) == 2


def test_source_ip():
    assert Traceroute.get_source_ip() == "192.168.0.106"
