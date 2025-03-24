import asyncio
import time
import logging
from api_executor import APIExecutor
from workflow_manager import APIWorkflowManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class APIWorkflow:
    def __init__(self, base_url, headers):
        """
        Initializes APIWorkflow and delegates execution to APIWorkflowManager.
        """
        self.api_executor = APIExecutor(base_url, headers)
        self.workflow_manager = APIWorkflowManager(base_url, headers)

    async def execute_api(self, method: str, endpoint: str, payload: dict = None):
        """
        Executes an API request, tracks execution time, and logs the result.
        """
        start_time = time.time()
        result = await self.api_executor.execute_api(method, endpoint, payload)
        result["execution_time"] = round(time.time() - start_time, 2)

        logging.info(f"✅ Executed {method} {endpoint} in {result['execution_time']}s -> Response: {result}")
        return result

    async def run_workflow(self, api_sequence):
        """
        Runs the API execution workflow using APIWorkflowManager.
        """
        logging.info(f"🚀 Running workflow with {len(api_sequence)} APIs.")
        return await self.workflow_manager.execute_workflow(api_sequence)
