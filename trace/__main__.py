import argparse

from trace.traceroute import Traceroute


def main():
    # Press the green button in the gutter to run the script.
    parser = argparse.ArgumentParser(description="Traceroute")
    parser.add_argument("host", default="yandex.com",
                        help="Host for trace")
    parser.add_argument("-f", "--first_ttl", dest="first_ttl", default=1,
                        help="Specifies with what TTL to start")
    parser.add_argument("-m", "--max_hops", type=int,
                        dest="max_hops", default=30,
                        help="Specifies the maximum number of hops.")
    parser.add_argument("-p", "--port", dest="port", default=33434,
                        help="Port")
    parser.add_argument("--time_for_receive",
                        type=int, dest="time_for_receive", default=1,
                        help="Sets the amount of time between requests")
    parser.add_argument("--number_of_request", type=int,
                        dest="number_of_request", default=3,
                        help="Sets the amount of request")
    parser.add_argument("--tcp", dest="tcp", action="store_true",
                        help="Sets the amount of request")
    parser.add_argument("--size", type=int, dest="size", default=40,
                        help="Sets the size packet")
    parser.add_argument("--payload", type=str, dest="payload", default="",
                        help="Sets the payload")
    parser.add_argument("--sendTime", type=int, dest="time_for_send",
                        default=1, help="Sets the payload")
    parser.add_argument("--seq", type=int, dest="seq",
                        default=1,
                        help="Sets the seq num")
    parser.add_argument("--interval", type=int, dest="interval",
                        default=0,
                        help="interval between requests")

    args = parser.parse_args()
    traceroute_util = Traceroute(max_hops=args.max_hops,
                                 port=args.port,
                                 host=args.host,
                                 number_of_request=args.number_of_request,
                                 time_for_receive=args.time_for_receive,
                                 ttl=args.first_ttl,
                                 tcp=args.tcp, packet_size=args.size,
                                 payload=args.payload,
                                 timeout_for_send=args.time_for_send,
                                 seq_number=args.seq,
                                 interval_per_request=args.interval)
    for i in traceroute_util.traceroute():
        print(i.trace_result)


if __name__ == "__main__":
    main()
