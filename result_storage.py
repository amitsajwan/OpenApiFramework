from langgraph.checkpoint.memory import MemorySaver

class ResultStorage:
    def __init__(self):
        """Initialize MemorySaver to store API execution results and created resource IDs."""
        self.memory = MemorySaver()

    def save_result(self, api_key, status_code, response_time, response_data):
        """Store API execution result with execution time and status."""
        self.memory.save(
            key=f"result_{api_key}",
            value={
                "status_code": status_code,
                "response_time": response_time,
                "response_data": response_data
            }
        )

    def get_result(self, api_key):
        """Retrieve execution result for a specific API."""
        return self.memory.get(f"result_{api_key}")

    def save_created_id(self, api_key, resource_id):
        """Store IDs of created resources for later deletion."""
        self.memory.save(f"created_id_{api_key}", resource_id)

    def get_created_id(self, api_key):
        """Retrieve stored resource ID for cleanup (DELETE request)."""
        return self.memory.get(f"created_id_{api_key}")

    def clear_results(self):
        """Clear all stored execution results."""
        self.memory.clear()

# Usage example
if __name__ == "__main__":
    storage = ResultStorage()
    
    # Simulating storing API execution results
    storage.save_result("POST /pet", 201, 0.45, {"id": 123, "name": "Fluffy"})
    storage.save_created_id("POST /pet", 123)
    
    # Retrieve results
    print("Execution Result:", storage.get_result("POST /pet"))
    print("Created Resource ID:", storage.get_created_id("POST /pet"))
