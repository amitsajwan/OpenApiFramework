from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import json

# Import your modules – ensure these files exist in your project structure.
from openapi_parser import OpenAPIParser
from llm_sequence_generator import LLMSequenceGenerator
from api_executor import APIExecutor
from workflow_manager import APIWorkflowManager
from visualization import get_execution_graph_json
from utils.result_storage import ResultStorage

app = FastAPI()

# Enable CORS for cross-origin requests (adjust allow_origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Global Initialization
# --------------------------

# OpenAPI file and base URL (update these as needed)
openapi_file_path = "openapi_specs/petstore.yaml"
base_url = "https://petstore.swagger.io/v2"  # Example base URL for Swagger Petstore
auth_headers = {}  # For any auth if required

# Initialize OpenAPI parser and extract API details
parser = OpenAPIParser(openapi_file_path)
api_map = parser.extract_api_details()  # Expects a dict with keys like "POST /pet", etc.

# Initialize LLM sequence generator (using Azure OpenAI; update credentials)
llm_gen = LLMSequenceGenerator(
    azure_endpoint="https://your-azure-endpoint.openai.azure.com/",
    azure_key="your-azure-key",
    deployment_name="your-deployment-name"
)
# Generate API execution order (an ordered list of API keys)
execution_sequence = llm_gen.generate_sequence(api_map)

# Initialize result storage
result_storage = ResultStorage()

# Initialize API Executor with base URL and auth headers
api_executor = APIExecutor(base_url, auth_headers)

# Initialize Workflow Manager with API map, execution sequence, base URL, and headers
workflow_manager = APIWorkflowManager(api_map, execution_sequence, base_url, auth_headers)

# --------------------------
# FastAPI Endpoints
# --------------------------

@app.get("/")
async def serve_index():
    """Serve the static index.html file for the chatbot UI."""
    return FileResponse("static/index.html")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for the chatbot UI to stream real-time updates."""
    await websocket.accept()
    try:
        await websocket.send_text("🔹 Welcome to the API Testing Chatbot!")
        await websocket.send_text("Type 'start' to begin API execution.")

        command = await websocket.receive_text()
        if command.lower() != "start":
            await websocket.send_text("⚠️ Unknown command. Closing connection.")
            await websocket.close()
            return

        # Notify user that execution is starting.
        await websocket.send_text("📂 Loading OpenAPI spec and generating execution sequence...")
        await websocket.send_text(f"✅ Extracted {len(api_map)} endpoints.")
        await websocket.send_text(f"🔄 Execution Sequence: {execution_sequence}")

        # Build and run the workflow
        workflow = workflow_manager.build_workflow()
        async for update in workflow_manager.run_workflow():
            # Each update is streamed in real-time to the client.
            await websocket.send_text(update)

        await websocket.send_text("✅ API Execution Completed!")
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

@app.get("/graph")
def graph_endpoint():
    """
    Returns the API execution graph in JSON format for visualization.
    This graph is built by the workflow manager.
    """
    graph_json = get_execution_graph_json(workflow_manager.execution_graph)
    return graph_json

# --------------------------
# Run the Application
# --------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
