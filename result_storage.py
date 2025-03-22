import json
import os

class ResultStorage:
    def __init__(self, storage_file="api_results.json"):
        """Initialize storage file to persist API execution results."""
        self.storage_file = storage_file
        if not os.path.exists(storage_file):
            with open(storage_file, "w") as f:
                json.dump({}, f)

    def save_result(self, api_key, status_code, response_time, response_data):
        """Store API execution result persistently."""
        with open(self.storage_file, "r") as f:
            data = json.load(f)
        data[api_key] = {
            "status_code": status_code,
            "response_time": response_time,
            "response_data": response_data
        }
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_result(self, api_key):
        """Retrieve execution result for a specific API."""
        with open(self.storage_file, "r") as f:
            data = json.load(f)
        return data.get(api_key, {"error": "No result found."})
