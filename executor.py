from langgraph.graph import Workflow
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

def execute_api(api_name, details):
    print(f"Executing {api_name} with details: {details}")
    return {"status": "success", "api": api_name}

workflow = Workflow()
workflow.add_node("execute_api", execute_api)

workflow.set_entry_point("execute_api")
