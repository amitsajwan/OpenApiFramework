import asyncio
import time
import logging
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from api_executor import APIExecutor
from llm_sequence_generator import LLMSequenceGenerator

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize MemorySaver for tracking execution results
memory = MemorySaver()

class APIWorkflow:
    def __init__(self, base_url, headers, use_llm=True):
        """
        Initialize API Workflow with APIExecutor and LangGraph state management.
        """
        self.api_executor = APIExecutor(base_url, headers)
        self.llm_generator = LLMSequenceGenerator() if use_llm else None
        self.workflow = StateGraph()

    async def execute_api(self, method: str, endpoint: str, payload: dict = None, is_first_run=True):
        """
        Execute an API request, track execution time, and store important response data.
        """
        start_time = time.time()
        
        # Generate payload using LLM (only for the first run)
        if is_first_run and self.llm_generator:
            payload = self.llm_generator.generate_payload(endpoint)
        else:
            payload = self.prepare_payload(method, endpoint, payload)

        try:
            result = await self.api_executor.execute_api(method, endpoint, payload)
            result["execution_time"] = round(time.time() - start_time, 2)

            # Store response data for dependent requests
            memory.save(f"{method} {endpoint}", result)
            if method == "POST" and "id" in result["response"]:
                memory.save(f"created_id_{endpoint}", result["response"]["id"])

            logging.info(f"Executed API: {method} {endpoint} -> {result}")
            return result
        except Exception as e:
            logging.error(f"Error executing API {method} {endpoint}: {str(e)}")
            return {"error": str(e), "execution_time": round(time.time() - start_time, 2)}

    def prepare_payload(self, method, endpoint, original_payload):
        """
        Modify payload by replacing placeholders with actual values from previous API responses.
        """
        if not original_payload:
            return None
        
        modified_payload = original_payload.copy()

        for key, value in modified_payload.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                placeholder = value.strip("{}")
                stored_value = memory.get(f"created_id_{placeholder}")
                if stored_value:
                    modified_payload[key] = stored_value
        
        return modified_payload

    def build_workflow(self, api_sequence, dependencies=None):
        """
        Build a LangGraph workflow dynamically, supporting parallel execution.
        """
        previous_api = None
        executing_tasks = {}

        for api in api_sequence:
            method, endpoint = api.split(" ", 1)

            async def node_fn(state, method=method, endpoint=endpoint):
                """
                Execute API inside LangGraph workflow and track execution results.
                """
                result = await self.execute_api(method, endpoint)
                state["last_api"] = endpoint  # Track last executed API
                return state

            self.workflow.add_node(endpoint, node_fn)

            if previous_api:
                if dependencies and endpoint in dependencies:
                    self.workflow.add_edge(dependencies[endpoint], endpoint)
                else:
                    executing_tasks[endpoint] = node_fn  # Allow parallel execution

            previous_api = endpoint

        async def run_parallel(state):
            await asyncio.gather(*[fn(state) for fn in executing_tasks.values()])
        
        self.workflow.add_node("parallel_execution", run_parallel)

        return self.workflow

    async def run_workflow(self, api_sequence, websocket=None):
        """
        Run the LangGraph workflow and stream execution updates to WebSocket.
        """
        workflow = self.build_workflow(api_sequence)

        async def execute_and_stream(state):
            for api in api_sequence:
                result = await self.execute_api(*api.split(" ", 1))
                
                # Stream real-time updates if WebSocket is connected
                if websocket:
                    await websocket.send_json({
                        "api": api, 
                        "status": result["status_code"], 
                        "time": result["execution_time"]
                    })
        
        await execute_and_stream({})

import asyncio
import time
import logging
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from api_executor import APIExecutor
from llm_sequence_generator import LLMSequenceGenerator

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize MemorySaver for tracking execution results
memory = MemorySaver()

class APIWorkflow:
    def __init__(self, base_url, headers, use_llm=True):
        """
        Initialize API Workflow with APIExecutor and LangGraph state management.
        """
        self.api_executor = APIExecutor(base_url, headers)
        self.llm_generator = LLMSequenceGenerator() if use_llm else None
        self.workflow = StateGraph()

    async def execute_api(self, method: str, endpoint: str, payload: dict = None, is_first_run=True):
        """
        Execute an API request, track execution time, and store important response data.
        """
        start_time = time.time()
        
        # Generate payload using LLM (only for the first run)
        if is_first_run and self.llm_generator:
            payload = self.llm_generator.generate_payload(endpoint)
        else:
            payload = self.prepare_payload(method, endpoint, payload)

        try:
            result = await self.api_executor.execute_api(method, endpoint, payload)
            result["execution_time"] = round(time.time() - start_time, 2)

            # Store response data for dependent requests
            memory.save(f"{method} {endpoint}", result)
            if method == "POST" and "id" in result["response"]:
                memory.save(f"created_id_{endpoint}", result["response"]["id"])

            logging.info(f"Executed API: {method} {endpoint} -> {result}")
            return result
        except Exception as e:
            logging.error(f"Error executing API {method} {endpoint}: {str(e)}")
            return {"error": str(e), "execution_time": round(time.time() - start_time, 2)}

    def prepare_payload(self, method, endpoint, original_payload):
        """
        Modify payload by replacing placeholders with actual values from previous API responses.
        """
        if not original_payload:
            return None
        
        modified_payload = original_payload.copy()

        for key, value in modified_payload.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                placeholder = value.strip("{}")
                stored_value = memory.get(f"created_id_{placeholder}")
                if stored_value:
                    modified_payload[key] = stored_value
        
        return modified_payload

    def build_workflow(self, api_sequence, dependencies=None):
        """
        Build a LangGraph workflow dynamically, supporting parallel execution.
        """
        previous_api = None
        executing_tasks = {}

        for api in api_sequence:
            method, endpoint = api.split(" ", 1)

            async def node_fn(state, method=method, endpoint=endpoint):
                """
                Execute API inside LangGraph workflow and track execution results.
                """
                result = await self.execute_api(method, endpoint)
                state["last_api"] = endpoint  # Track last executed API
                return state

            self.workflow.add_node(endpoint, node_fn)

            if previous_api:
                if dependencies and endpoint in dependencies:
                    self.workflow.add_edge(dependencies[endpoint], endpoint)
                else:
                    executing_tasks[endpoint] = node_fn  # Allow parallel execution

            previous_api = endpoint

        async def run_parallel(state):
            await asyncio.gather(*[fn(state) for fn in executing_tasks.values()])
        
        self.workflow.add_node("parallel_execution", run_parallel)

        return self.workflow

    async def run_workflow(self, api_sequence, websocket=None):
        """
        Run the LangGraph workflow and stream execution updates to WebSocket.
        """
        workflow = self.build_workflow(api_sequence)

        async def execute_and_stream(state):
            for api in api_sequence:
                result = await self.execute_api(*api.split(" ", 1))
                
                # Stream real-time updates if WebSocket is connected
                if websocket:
                    await websocket.send_json({
                        "api": api, 
                        "status": result["status_code"], 
                        "time": result["execution_time"]
                    })
        
        await execute_and_stream({})
