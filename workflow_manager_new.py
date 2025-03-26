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
def build_workflow(self, llm_graph, api_map):
    """
    Constructs the execution workflow from the LLM-generated DAG (Directed Acyclic Graph).
    Uses api_map to get method & endpoint from operation ID.
    
    llm_graph = {
        "nodes": ["createPet", "getPetById", "listPets"],  # Operation IDs
        "edges": [["createPet", "getPetById"], ["createPet", "listPets"]]  # Dependencies
    }
    """
    # ✅ Create nodes
    for operation_id in llm_graph["nodes"]:
        api_details = api_map.get(operation_id)  # Get API method & path
        if not api_details:
            logging.error(f"❌ API not found in OpenAPI spec: {operation_id}")
            continue

        method = api_details["method"]
        endpoint = api_details["path"]

        async def node_fn(state, method=method, endpoint=endpoint, operation_id=operation_id):
            """
            Executes the API call and updates the state.
            """
            # Extract previous API response data if available
            dependent_responses = {
                dep: state.responses.get(dep, {}) for dep in llm_graph["edges"] if dep[1] == operation_id
            }

            # Merge responses into a single payload
            merged_payload = {**dependent_responses}

            # Execute API call
            result = await state.executor.execute_api(method, endpoint, merged_payload)

            # ✅ Store API response in state for future nodes
            state.responses[operation_id] = result
            return state

        # ✅ Add node with operation ID
        self.graph.add_node(operation_id, node_fn)

    # ✅ Create edges from LLM DAG
    for src, dest in llm_graph["edges"]:
        self.graph.add_edge(src, dest)

    return self.graph
    
async def execute_workflow(self, api_sequence):
        """
        Executes the workflow using LangGraph.
        """
        self.build_workflow(api_sequence)
        state = ApiExecutionState()  # ✅ Ensure correct state is used
        return await self.graph.run(state)
