import requests
import time

class APIExecutor:
    def __init__(self, base_url, headers, api_map):
        self.base_url = base_url
        self.headers = headers
        self.api_map = api_map
        self.execution_results = {}

    def send_request(self, method, endpoint, payload=None, params=None):
        """Send an API request and return response details."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=payload,
            params=params
        )

        elapsed_time = round(time.time() - start_time, 3)

        result = {
            "status_code": response.status_code,
            "response_time": elapsed_time,
            "response_body": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
        }

        return result

    def execute_api_sequence(self, sequence):
        """Execute APIs in the given sequence."""
        print("\nExecuting API sequence...\n")
        for api_key in sequence:
            method, endpoint = api_key.split(" ", 1)
            api_details = self.api_map.get(api_key, {})

            payload = None
            if method in ["POST", "PUT"]:
                payload = generate_payload(api_details.get("requestBody", {}), self.api_map)

            result = self.send_request(method, endpoint, payload=payload)
            self.execution_results[api_key] = result
            
            print(f"{method} {endpoint} → Status: {result['status_code']}, Time: {result['response_time']}s")

        return self.execution_results
      
