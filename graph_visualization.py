import networkx as nx
import matplotlib.pyplot as plt
import asyncio
import websockets
import json

class APIGraphVisualizer:
    def __init__(self):
        """
        Initializes the API execution graph visualizer.
        """
        self.graph = nx.DiGraph()  # ✅ Directed graph for API execution flow

    def add_api_dependency(self, from_api, to_api):
        """
        Adds a dependency between API calls dynamically.
        """
        self.graph.add_edge(from_api, to_api)
        self.update_visualization()

    def update_visualization(self, title="API Execution Flow"):
        """
        Generates and refreshes the API execution graph dynamically.
        """
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color="lightblue", edge_color="gray",
                node_size=2500, font_size=10, font_weight="bold", arrows=True)
        plt.title(title)
        plt.draw()
        plt.pause(0.1)  # ✅ Refresh without blocking execution

    def get_execution_graph_json(self):
        """
        Returns the execution graph as JSON (for FastAPI `/graph` endpoint).
        """
        graph_data = {
            "nodes": list(self.graph.nodes),
            "edges": list(self.graph.edges)
        }
        return graph_data  # ✅ Now properly defined!

    async def websocket_listener(self, uri="ws://localhost:8000/ws"):
        """
        Listens for real-time API execution updates via WebSockets.
        """
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                from_api, to_api = data.get("from"), data.get("to")
                
                if from_api and to_api:
                    print(f"🔄 Updating graph: {from_api} -> {to_api}")
                    self.add_api_dependency(from_api, to_api)

# ✅ Run the visualizer
if __name__ == "__main__":
    visualizer = APIGraphVisualizer()
    plt.ion()  # ✅ Enable interactive mode for live updates
    asyncio.run(visualizer.websocket_listener())
