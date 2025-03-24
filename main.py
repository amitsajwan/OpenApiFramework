from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import json
import logging
from openapi_parser import OpenAPIParser
from llm_sequence_generator import LLMSequenceGenerator
from api_executor import APIExecutor
from api_workflow import APIWorkflow
from graph_visualization import APIGraphVisualizer
from utils.result_storage import ResultStorage

app = FastAPI()

# Enable CORS
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

# Initialize components
parser = OpenAPIParser(openapi_file_path)
api_map = parser.get_all_endpoints()
llm_gen = LLMSequenceGenerator()
execution_sequence = llm_gen.generate_sequence(api_map)
result_storage = ResultStorage()
api_executor = APIExecutor(base_url, auth_headers)
workflow_manager = APIWorkflow(base_url, auth_headers, websocket_uri="ws://localhost:8000/ws")
visualizer = APIGraphVisualizer()

# Store connected WebSocket clients
connected_clients = set()

# --------------------------
# FastAPI Endpoints
# --------------------------

@app.get("/")
async def serve_index():
    """Serve the unified chat & graph visualization UI."""
    return FileResponse("static/index.html")  # ✅ Common UI page

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for real-time API execution updates."""
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        await websocket.send_json({"message": "Welcome to API Testing! Type 'start' to begin."})
        command = await websocket.receive_text()
        if command.lower() != "start":
            await websocket.send_json({"message": "Invalid command. Closing connection."})
            await websocket.close()
            return

        await websocket.send_json({"message": f"Extracted {len(api_map)} endpoints."})
        await websocket.send_json({"message": f"Execution Sequence: {execution_sequence}"})

        prev_api = None
        for api in execution_sequence:
            result = await workflow_manager.execute_api(*api.split(" ", 1))
            
            # Update visualization
            if prev_api:
                await broadcast_update({"from": prev_api, "to": api})
                visualizer.add_api_dependency(prev_api, api)

            prev_api = api

            # Send real-time execution updates
            await websocket.send_json({
                "api": api, 
                "status": result["status_code"], 
                "time": result["execution_time"]
            })

        await websocket.send_json({"message": "✅ API Execution Completed!"})
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected.")
    finally:
        connected_clients.remove(websocket)

@app.get("/graph")
async def graph_endpoint():
    """Returns the execution graph in JSON format."""
    return visualizer.get_execution_graph_json()

async def broadcast_update(update_data):
    """Sends execution updates to all WebSocket clients."""
    if connected_clients:
        message = json.dumps(update_data)
        await asyncio.gather(*[client.send_text(message) for client in connected_clients])

# --------------------------
# Run the Application
# --------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
