from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from api_executor import APIExecutor

memory = MemorySaver()

class APIWorkflow:
    def __init__(self, api_executor, sequence):
        self.api_executor = api_executor
        self.sequence = sequence
        self.workflow = StateGraph()

    @tool
    def execute_api(api_key: str):
        """Execute a single API request and store the result."""
        result = api_executor.send_request(*api_key.split(" ", 1))
        memory.save(api_key, result)
        return result

    @tool
    def user_intervention(api_key: str):
        """Ask the user whether to proceed at critical steps."""
        decision = input(f"Proceed with {api_key}? (yes/no): ")
        return decision.lower() == "yes"

    def build_workflow(self):
        """Create LangGraph workflow with execution order."""
        prev_node = None
        for api_key in self.sequence:
            node = self.workflow.add_node(api_key, self.execute_api, api_key=api_key)

            if "POST" in api_key or "DELETE" in api_key:
                intervention_node = self.workflow.add_node(f"intervene_{api_key}", self.user_intervention, api_key=api_key)
                self.workflow.add_edge(intervention_node, node)

            if prev_node:
                self.workflow.add_edge(prev_node, node)

            prev_node = node

    def run(self):
        """Compile and execute the workflow."""
        self.workflow.compile()
        self.workflow.invoke()
      
