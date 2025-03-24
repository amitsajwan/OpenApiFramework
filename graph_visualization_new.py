import networkx as nx
import json
import logging

logging.basicConfig(level=logging.INFO)

class APIGraphVisualizer:
    def __init__(self):
        """
        Initializes API execution graph visualizer.
        """
        self.graph = nx.DiGraph()
        self.nodes = set()
        self.edges = set()

    def add_api_dependency(self, from_api, to_api):
        """
        Adds an execution dependency between APIs.
        """
        if from_api not in self.nodes:
            self.nodes.add(from_api)
            self.graph.add_node(from_api)
            logging.info(f"🟢 Added node: {from_api}")

        if to_api not in self.nodes:
            self.nodes.add(to_api)
            self.graph.add_node(to_api)
            logging.info(f"🟢 Added node: {to_api}")

        if (from_api, to_api) not in self.edges:
            self.edges.add((from_api, to_api))
            self.graph.add_edge(from_api, to_api)
            logging.info(f"🔗 Added edge: {from_api} → {to_api}")

    def get_execution_graph_json(self):
        """
        Returns the execution graph as JSON for frontend visualization.
        Ensures nodes and edges are always included.
        """
        if not self.nodes or not self.edges:
            logging.warning("⚠️ No nodes or edges in DAG!")
            return json.dumps({"message": "No execution graph available", "nodes": [], "edges": []})

        nodes = [{"id": node} for node in self.nodes]
        edges = [{"source": edge[0], "target": edge[1]} for edge in self.edges]

        logging.info(f"📊 Returning DAG with {len(nodes)} nodes & {len(edges)} edges.")
        return json.dumps({"nodes": nodes, "edges": edges})

    def reset_graph(self):
        """
        Clears the DAG, useful when a new sequence is selected.
        """
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        logging.info("🗑️ Execution graph reset.")
