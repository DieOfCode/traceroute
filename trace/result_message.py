class ResultMessage:
    def __init__(self, results, ttl, icmp_type, icmp_code, tcp_flag):
        self.ttl: int = ttl
        self.icmp_type: int = icmp_type
        self.icmp_code: int = icmp_code
        self.tcp_flag = tcp_flag
        self.results = results

    def __str__(self) -> str:
        first_string = f"{self.ttl}:{self.results[0]}"
        self.results[0] = first_string
        return " ".join(self.results)
