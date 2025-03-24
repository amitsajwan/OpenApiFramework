import asyncio
import logging
from langgraph.graph import StateGraph
from state import APIExecutionState
from api_executor import APIExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class APIWorkflowManager:
    def __init__(self, base_url, headers):
        """
        Initializes the API workflow using StateGraph from state.py.
        ✅ Passes the graph as an argument.
        """
        self.api_executor = APIExecutor(base_url, headers)
        self.execution_state = APIExecutionState()  # ✅ Uses the modified StateGraph from state.py
        self.state_graph = StateGraph(state_schema=self.execution_state.state_schema)  # ✅ Passes state schema

    def add_api_node(self, method, endpoint):
        """
        Adds an API execution step as a node in the workflow.
        """
        async def node_fn(state):
            result = await self.api_executor.execute_api(method, endpoint)
            self.execution_state.save_result(f"{method} {endpoint}", result)
            state["last_api"] = endpoint  # Track last executed API
            return state

        self.state_graph.add_node(endpoint, node_fn, input="last_api", output="next_api")  # ✅ Defines input/output

    def add_dependency(self, from_api, to_api):
        """
        Adds an execution dependency between API nodes.
        """
        self.state_graph.add_edge(from_api, to_api)  # ✅ Properly links nodes using StateGraph

    async def execute_workflow(self, api_sequence):
        """
        Executes the API workflow using the structured graph.
        """
        for i in range(len(api_sequence) - 1):
            self.add_api_node(*api_sequence[i].split(" ", 1))
            self.add_dependency(api_sequence[i], api_sequence[i + 1])

        async def execute_graph(state):
            return await self.state_graph.execute(state)  # ✅ Executes workflow with proper state handling

        return await execute_graph({"last_api": None})

# Example Usage
if __name__ == "__main__":
    base_url = "https://petstore.swagger.io/v2"
    headers = {"Content-Type": "application/json"}
    
    workflow_manager = APIWorkflowManager(base_url, headers)

    api_sequence = [
        "POST /pet",
        "GET /pet/{id}",
        "PUT /pet/{id}",
        "DELETE /pet/{id}"
    ]

    asyncio.run(workflow_manager.execute_workflow(api_sequence))
