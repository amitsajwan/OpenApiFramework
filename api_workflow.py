import asyncio
import logging
from api_executor import APIExecutor
from workflow_manager import APIWorkflowManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class APIWorkflow:
    def __init__(self, base_url, headers):
        """
        Initializes the API workflow and delegates execution to APIWorkflowManager.
        """
        self.api_executor = APIExecutor(base_url, headers)
        self.workflow_manager = APIWorkflowManager(base_url, headers)  # ✅ Uses Workflow Manager

    async def execute_api(self, method: str, endpoint: str, payload: dict = None, is_first_run=True):
        """
        Executes an API request and tracks execution state.
        """
        result = await self.api_executor.execute_api(method, endpoint, payload)
        logging.info(f"Executed API: {method} {endpoint} -> {result}")
        return result

    def prepare_payload(self, method, endpoint, original_payload):
        """
        Modifies payload by replacing placeholders with actual values from previous API responses.
        """
        if not original_payload:
            return None

        modified_payload = original_payload.copy()
        for key, value in modified_payload.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                placeholder = value.strip("{}")
                stored_value = self.workflow_manager.execution_state.get_created_id(placeholder)
                if stored_value:
                    modified_payload[key] = stored_value
        
        return modified_payload

    async def run_workflow(self, api_sequence):
        """
        Runs the API execution workflow using APIWorkflowManager.
        """
        logging.info(f"Starting workflow execution for {len(api_sequence)} APIs.")
        return await self.workflow_manager.execute_workflow(api_sequence)

# Example Usage
if __name__ == "__main__":
    base_url = "https://petstore.swagger.io/v2"
    headers = {"Content-Type": "application/json"}
    
    api_workflow = APIWorkflow(base_url, headers)

    api_sequence = [
        "POST /pet",
        "GET /pet/{id}",
        "PUT /pet/{id}",
        "DELETE /pet/{id}"
    ]

    asyncio.run(api_workflow.run_workflow(api_sequence))
