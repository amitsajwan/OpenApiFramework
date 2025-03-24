import asyncio
import logging
from langgraph.graph import StateGraph
from api_executor import APIExecutor
from pydantic import BaseModel
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class APIExecutionState(BaseModel):
    """
    Defines the execution state for the API testing workflow.
    """
    last_api: Optional[str] = None  # Last executed API
    next_api: Optional[str] = None  # Next API to execute
    execution_results: Dict[str, Dict] = {}  # Stores API responses & status codes

class APIWorkflowManager:
    def __init__(self, base_url, headers):
        """
        Initializes APIWorkflowManager with a correctly defined StateGraph.
        ✅ Fix: Passes APIExecutionState as schema for StateGraph.
        """
        self.api_executor = APIExecutor(base_url, headers)
        self.state_graph = StateGraph(APIExecutionState)  # ✅ Correct initialization

    def add_api_node(self, method, endpoint):
        """
        Adds an API execution step as a node in the workflow.
        """
        async def node_fn(state: APIExecutionState):
            result = await self.api_executor.execute_api(method, endpoint)
            state.execution_results[f"{method} {endpoint}"] = result  # Store result
            state.last_api = endpoint  # Update last API executed
            return state

        self.state_graph.add_node(endpoint, node_fn, input="last_api", output="next_api")

    def add_dependency(self, from_api, to_api):
        """
        Adds an execution dependency between API nodes.
        """
        self.state_graph.add_edge(from_api, to_api)  # ✅ Properly links nodes using StateGraph

    async def execute_workflow(self, api_sequence):
        """
        Executes the API workflow in order while tracking execution state.
        """
        for i in range(len(api_sequence) - 1):
            self.add_api_node(*api_sequence[i].split(" ", 1))
            self.add_dependency(api_sequence[i], api_sequence[i + 1])

        async def execute_graph(state: APIExecutionState):
            return await self.state_graph.execute(state)  # ✅ Executes workflow correctly

        return await execute_graph(APIExecutionState())  # ✅ Correctly initializes the state
