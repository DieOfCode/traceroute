import argparse
from trace_util.traceroute import Traceroute
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Traceroute")
    parser.add_argument("--host", dest="host", default="127.0.0.1",help="Host for traceroute")
    parser.add_argument("-f", "--first_ttl", dest="first_ttl", default=1, help="Specifies with what TTL to start")
    parser.add_argument("-m", "--max_hops",type= int, dest="max_ttl", default=30, help="Specifies the maximum number of hops.")
    parser.add_argument("-p", "--port", dest="port", default=33434, help="Port")
    args = parser.parse_args()
    traceroute_util = Traceroute( first_ttl=args.first_ttl,
                                            max_hops=args.max_ttl, port=args.port,host=args.host)
    for i in traceroute_util.traceroute():
        print(i)

