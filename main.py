import argparse
from trace_util.traceroute import Traceroute

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Traceroute")
    parser.add_argument("--host", dest="host", default="google.com", help="Host for traceroute")
    parser.add_argument("-f", "--first_ttl", dest="first_ttl", default=1, help="Specifies with what TTL to start")
    parser.add_argument("-m", "--max_hops", type=int, dest="max_hops", default=30,
                        help="Specifies the maximum number of hops.")
    parser.add_argument("-p", "--port", dest="port", default=33434, help="Port")
    parser.add_argument("--time_per_request", type=int, dest="time_per_request", default=0,
                        help="Sets the amount of time between requests")
    parser.add_argument("--number_of_request", type=int, dest="number_of_request", default=3,
                        help="Sets the amount of request")
    args = parser.parse_args()
    traceroute_util = Traceroute(first_ttl=args.first_ttl,
                                 max_hops=args.max_hops, port=args.port, host=args.host,
                                 number_of_request=args.number_of_request, time_per_request=args.time_per_request)
    for i in traceroute_util.traceroute():
        print(i.trace_result)
