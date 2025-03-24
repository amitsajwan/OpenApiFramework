from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import json
import logging
import websockets

# Import your modules
from openapi_parser import OpenAPIParser
from llm_sequence_generator import LLMSequenceGenerator
from api_executor import APIExecutor
from api_workflow import APIWorkflow
from graph_visualization import APIGraphVisualizer
from utils.result_storage import ResultStorage

app = FastAPI()

# Enable CORS for cross-origin requests
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

openapi_file_path = "openapi_specs/petstore.yaml"
base_url = "https://petstore.swagger.io/v2"
auth_headers = {}

# Initialize OpenAPI parser and extract API details
parser = OpenAPIParser(openapi_file_path)
api_map = parser.get_all_endpoints()

# Initialize LLM sequence generator
llm_gen = LLMSequenceGenerator()
execution_sequence = llm_gen.generate_sequence(api_map)

# Initialize result storage
result_storage = ResultStorage()

# Initialize API Executor
api_executor = APIExecutor(base_url, auth_headers)

# Initialize API Workflow Manager
workflow_manager = APIWorkflow(base_url, auth_headers, websocket_uri="ws://localhost:8000/ws")

# Initialize API Graph Visualizer
visualizer = APIGraphVisualizer()

# WebSocket connections storage
connected_clients = set()

# --------------------------
# FastAPI Endpoints
# --------------------------

@app.get("/")
async def serve_index():
    """Serve the static index.html file for the chatbot UI."""
    return FileResponse("static/index.html")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates and chatbot interaction."""
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        await websocket.send_text("🔹 Welcome to the API Testing Chatbot!")
        await websocket.send_text("Type 'start' to begin API execution.")

        command = await websocket.receive_text()
        if command.lower() != "start":
            await websocket.send_text("⚠️ Unknown command. Closing connection.")
            await websocket.close()
            return

        await websocket.send_text("📂 Loading OpenAPI spec and generating execution sequence...")
        await websocket.send_text(f"✅ Extracted {len(api_map)} endpoints.")
        await websocket.send_text(f"🔄 Execution Sequence: {execution_sequence}")

        # Run the workflow and send real-time updates
        prev_api = None
        for api in execution_sequence:
            result = await workflow_manager.execute_api(*api.split(" ", 1))
            
            # Update visualization graph
            if prev_api:
                await broadcast_update({"from": prev_api, "to": api})
                visualizer.add_api_dependency(prev_api, api)

            prev_api = api

            # Stream execution results
            await websocket.send_text(f"✅ Executed: {api} | Status: {result['status_code']} | Time: {result['execution_time']}s")

        await websocket.send_text("✅ API Execution Completed!")
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected.")
    finally:
        connected_clients.remove(websocket)

@app.get("/graph")
def graph_endpoint():
    """
    Returns the API execution graph in JSON format for visualization.
    """
    graph_json = visualizer.get_execution_graph_json()
    return graph_json

async def broadcast_update(update_data):
    """
    Sends execution updates to all connected WebSocket clients.
    """
    if connected_clients:
        message = json.dumps(update_data)
        await asyncio.gather(*[client.send_text(message) for client in connected_clients])

# --------------------------
# Run the Application
# --------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
