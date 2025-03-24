import logging
from langgraph.graph import StateGraph
from state import ApiExecutionState  # ✅ Must be passed into StateGraph

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class APIWorkflowManager:
    def __init__(self, base_url, headers):
        """
        Initializes API Workflow Manager using LangGraph and ApiExecutionState.
        """
        self.base_url = base_url
        self.headers = headers
        self.graph = StateGraph(ApiExecutionState)  # ✅ Passing ApiExecutionState is mandatory

    def build_workflow(self, api_sequence):
        """
        Constructs the execution workflow from the user-modified DAG sequence.
        """
        previous_api = None

        for api in api_sequence:
            method, endpoint = api.split(" ", 1)

            async def node_fn(state, method=method, endpoint=endpoint):
                result = await state.executor.execute_api(method, endpoint)
                state.last_api = endpoint
                return state

            self.graph.add_node(endpoint, node_fn)

            if previous_api:
                self.graph.add_edge(previous_api, endpoint)

            previous_api = endpoint

        return self.graph

    async def execute_workflow(self, api_sequence):
        """
        Executes the workflow using LangGraph.
        """
        self.build_workflow(api_sequence)
        state = ApiExecutionState()  # ✅ Ensure correct state is used
        return await self.graph.run(state)
