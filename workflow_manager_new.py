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
    Uses api_map to get method & endpoint from operation ID.
    """
    previous_api = None

    for operation_id in api_sequence:
        api_details = api_map.get(operation_id)  # ✅ Get method & path from api_map
        if not api_details:
            logging.error(f"❌ API not found in OpenAPI spec: {operation_id}")
            continue

        method = api_details["method"]
        endpoint = api_details["path"]

        async def node_fn(state, method=method, endpoint=endpoint):
            result = await state.executor.execute_api(method, endpoint)
            state.last_api = endpoint
            return state

        self.graph.add_node(operation_id, node_fn)  # ✅ Use operation ID as node name

        if previous_api:
            self.graph.add_edge(previous_api, operation_id)  # ✅ Maintain sequence

        previous_api = operation_id

    return self.graph

    
async def execute_workflow(self, api_sequence):
        """
        Executes the workflow using LangGraph.
        """
        self.build_workflow(api_sequence)
        state = ApiExecutionState()  # ✅ Ensure correct state is used
        return await self.graph.run(state)
