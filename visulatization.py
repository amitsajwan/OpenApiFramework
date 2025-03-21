import networkx as nx
from networkx.readwrite import json_graph

def get_execution_graph_json(execution_graph: nx.DiGraph):
    """
    Converts a NetworkX DiGraph into JSON (node-link format) for visualization.
    """
    return json_graph.node_link_data(execution_graph)
