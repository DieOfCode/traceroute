class ResultMessage:
    def __init__(self, results,ttl,icmp_type, icmp_code):
        self.ttl:int = ttl
        self.icmp_type: int = icmp_type
        self.icmp_code: int = icmp_code
        self.trace_result = self.update_result(results)

    def update_result(self,results):
        first_string = f"{self.ttl}:{results[0]}"
        results[0] = first_string
        return " ".join(results)

