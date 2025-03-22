from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from api_executor import APIExecutor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

memory = MemorySaver()

class APIWorkflow:
    def __init__(self, api_executor, sequence):
        self.api_executor = api_executor
        self.sequence = sequence
        self.workflow = StateGraph()

    @tool
    def execute_api(api_key: str):
        """Execute a single API request and store the result."""
        try:
            result = api_executor.send_request(*api_key.split(" ", 1))
            memory.save(api_key, result)
            logging.info(f"Executed API: {api_key} -> Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error executing API {api_key}: {str(e)}")
            return {"error": str(e)}
