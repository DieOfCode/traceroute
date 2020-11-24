from trace.result_message import ResultMessage


def test_result_message():
    test_message = ResultMessage(ttl=1, icmp_type=0, icmp_code=0, tcp_flag=0,
                                 results=[
                                     'b1-lo1.system-ural.ru (194.28.225.254) '
                                     '11ms ',
                                     'b1-lo1.system-ural.ru (194.28.225.254) '
                                     '23ms ',
                                     'b1-lo1.system-ural.ru (194.28.225.254) '
                                     '23ms '])
    assert test_message.__str__() == "1:b1-lo1.system-ural.ru (" \
                                     "194.28.225.254) " \
                                     "11ms  b1-lo1.system-ural.ru (" \
                                     "194.28.225.254) 23ms  " \
                                     "b1-lo1.system-ural.ru " \
                                     "(194.28.225.254) 23ms "
