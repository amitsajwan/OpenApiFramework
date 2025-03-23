import networkx as nx
import matplotlib.pyplot as plt

class APIGraphVisualizer:
    def __init__(self):
        """
        Initialize the graph visualizer for API execution flow.
        """
        self.graph = nx.DiGraph()  # Directed graph

    def add_api_dependency(self, from_api, to_api):
        """
        Add a dependency between API calls.
        
        :param from_api: The first API call (e.g., "POST /pet")
        :param to_api: The dependent API call (e.g., "GET /pet/{id}")
        """
        self.graph.add_edge(from_api, to_api)

    def visualize(self, title="API Execution Flow"):
        """
        Generate and display the API execution graph.
        """
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(self.graph)  # Auto-layout positioning
        nx.draw(
            self.graph, pos, with_labels=True, node_color="lightblue", edge_color="gray",
            node_size=2500, font_size=10, font_weight="bold", arrows=True
        )
        plt.title(title)
        plt.show()

# Example Usage
if __name__ == "__main__":
    visualizer = APIGraphVisualizer()
    
    # Sample API execution flow
    visualizer.add_api_dependency("POST /pet", "GET /pet/{id}")
    visualizer.add_api_dependency("GET /pet/{id}", "PUT /pet/{id}")
    visualizer.add_api_dependency("PUT /pet/{id}", "DELETE /pet/{id}")
    
    visualizer.visualize()
  
