import asyncio
import networkx as nx
from langgraph.graph import StateGraph  # Adjust if your LangGraph API is different
from api_executor import APIExecutor  # Assumes APIExecutor.execute_api(api_name, api_details, context)
from utils.result_storage import ResultStorage

class APIWorkflowManager:
    def __init__(self, api_map, execution_sequence, base_url, headers):
        """
        :param api_map: Dictionary with API details. Keys like "POST /pet" mapping to dicts with at least:
                        { "method": "POST", "path": "/pet", "parameters": ..., "request_body": ... }
        :param execution_sequence: Ordered list of API names (e.g. ["POST /pet", "GET /pet/{petId}", ...])
        :param base_url: The API's base URL.
        :param headers: Authentication headers.
        """
        self.api_map = api_map
        self.execution_sequence = execution_sequence
        self.base_url = base_url
        self.headers = headers
        self.workflow = StateGraph()
        self.execution_graph = nx.DiGraph()  # For visualization
        self.executor = APIExecutor(base_url, headers)
        self.storage = ResultStorage()

    def build_workflow(self):
        """
        Constructs the LangGraph workflow from the execution sequence.
        Each node executes an API call and updates context (e.g., saving created IDs).
        """
        previous_api = None
        for api_name in self.execution_sequence:
            # Define the node function to execute an API call
            async def node_fn(state, api_name=api_name):
                # Execute the API call with the given context.
                # This method should handle passing created IDs from previous responses.
                result = await self.executor.execute_api(api_name, self.api_map[api_name], state)
                
                # If this is a POST and the response contains an ID, store it in the context.
                if self.api_map[api_name]["method"] == "POST" and "id" in result:
                    state["created_id"] = result["id"]
                
                # Update the visualization graph:
                self.execution_graph.add_node(api_name, status="executed")
                if state.get("last_api"):
                    self.execution_graph.add_edge(state["last_api"], api_name)
                state["last_api"] = api_name
                return state

            # Add the node to the workflow
            self.workflow.add_node(api_name, node_fn)
            # Connect nodes sequentially
            if previous_api:
                self.workflow.add_edge(previous_api, api_name)
            previous_api = api_name

        return self.workflow

    async def run_workflow(self):
        """
        Executes the workflow and streams status updates.
        Yields a message for each node as it completes.
        """
        state = {}
        workflow = self.build_workflow()
        async for update in workflow.invoke(state):  # Assume invoke() yields updates/messages
            yield update
        # Save final execution results in storage.
        self.storage.save_results(state)

    def get_execution_graph_json(self):
        """
        Returns the execution graph (NetworkX DiGraph) in JSON format for visualization.
        """
        from networkx.readwrite import json_graph
        return json_graph.node_link_data(self.execution_graph)
      
