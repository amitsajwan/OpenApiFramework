import asyncio
import networkx as nx
import matplotlib.pyplot as plt
from langgraph.graph import StateGraph
from api_executor import APIExecutor
from utils.result_storage import ResultStorage

class APIWorkflowManager:
    def __init__(self, api_map, execution_sequence, base_url, headers):
        self.api_map = api_map
        self.execution_sequence = execution_sequence
        self.base_url = base_url
        self.headers = headers
        self.workflow = StateGraph()
        self.execution_graph = nx.DiGraph()  # For visualization
        self.executor = APIExecutor(base_url, headers)
        self.storage = ResultStorage()
        self.result_queue = asyncio.Queue()  # For real-time streaming

    async def confirm_start(self):
        user_input = input("Start API Execution? (yes/no): ").strip().lower()
        return user_input == "yes"

    async def execute_workflow(self):
        if not await self.confirm_start():
            print("Execution aborted by user.")
            return

        previous_api = None
        for api_name in self.execution_sequence:
            async def node_fn(state, api_name=api_name):
                result = await self.executor.execute_api(api_name, self.api_map[api_name], state)
                await self.result_queue.put((api_name, result))  # Stream result
                
                if self.api_map[api_name]["method"] == "POST" and "id" in result:
                    state["created_id"] = result["id"]

                self.execution_graph.add_node(api_name, status="executed")
                if state.get("last_api"):
                    self.execution_graph.add_edge(state["last_api"], api_name)
                state["last_api"] = api_name
                return state

            self.workflow.add_node(api_name, node_fn)
            if previous_api:
                self.workflow.add_edge(previous_api, api_name)
            previous_api = api_name

        await self.workflow.run({})

    async def stream_results(self):
        while True:
            api_name, result = await self.result_queue.get()
            print(f"API: {api_name} -> Result: {result}")
            self.result_queue.task_done()

    def visualize_execution_graph(self):
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(self.execution_graph)
        nx.draw(self.execution_graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
        plt.title("API Execution Flow")
        plt.show()
