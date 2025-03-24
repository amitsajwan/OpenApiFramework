import networkx as nx
import json

class APIGraphVisualizer:
    def __init__(self):
        """Initializes the API execution graph visualizer."""
        self.graph = nx.DiGraph()  # Directed graph for execution flow

    def add_api_dependency(self, from_api, to_api):
        """Adds a dependency between API calls."""
        self.graph.add_edge(from_api, to_api)

    def get_execution_graph_json(self):
        """
        Returns the execution graph in a format usable by the frontend.
        """
        nodes = [{"id": node} for node in self.graph.nodes]
        edges = [{"source": edge[0], "target": edge[1]} for edge in self.graph.edges]

        return json.dumps({"nodes": nodes, "edges": edges})
