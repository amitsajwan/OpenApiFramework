from pydantic import BaseModel
from typing import Optional, Dict, List
import time

class APIExecutionState(BaseModel):
    """
    Tracks API execution metrics during load testing.
    """
    last_api: Optional[str] = None  # Last executed API
    next_api: Optional[str] = None  # Next API to execute
    execution_results: Dict[str, Dict] = {}  # Stores API responses & status codes
    api_metrics: Dict[str, Dict[str, float]] = {}  # Stores API timing & counts
    start_time: float = time.time()  # Track start time of execution

    def log_api_execution(self, api_name: str, response_time: float):
        """
        Logs execution time and request count for an API.
        """
        if api_name not in self.api_metrics:
            self.api_metrics[api_name] = {"count": 0, "total_time": 0.0}

        self.api_metrics[api_name]["count"] += 1
        self.api_metrics[api_name]["total_time"] += response_time



async def run_load_test():
    """
    Runs a load test with 100 concurrent users using LangGraph.
    """
    chain = langgraph.compile()  # Compile workflow
    states = [APIExecutionState() for _ in range(100)]  # Create 100 state instances

    async for result in chain.abatch(states, stream_mode="values"):
        print(result)  # Process each result

    generate_report(states)  # Generate performance report

# Run load test
asyncio.run(run_load_test())



import asyncio

async def execute_api(state: APIExecutionState, api_name: str, request_func):
    """
    Executes an API, records execution time, and updates state.
    """
    start_time = time.time()  # Start timing
    response = await request_func()  # Simulate API request (Replace with actual API call)
    end_time = time.time()  # End timing

    # Calculate execution time
    execution_time = end_time - start_time

    # Log API execution metrics
    state.log_api_execution(api_name, execution_time)

    # Store result
    state.execution_results[api_name] = {
        "status": response.status_code if response else "Unknown",
        "time_taken": execution_time
    }

    return state
