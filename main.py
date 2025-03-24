from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import json
import logging
from pathlib import Path  # ✅ To serve index.html properly
from openapi_parser import OpenAPIParser
from workflow_manager import APIWorkflowManager
from graph_visualization import APIGraphVisualizer

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

parser = OpenAPIParser(openapi_file_path)
api_map = parser.get_all_endpoints()
workflow_manager = APIWorkflowManager(base_url, auth_headers)
visualizer = APIGraphVisualizer()
connected_clients = set()
dag_sequence = []  # Stores the user-modified execution order

# --------------------------
# Serve UI (index.html)
# --------------------------

@app.get("/")
async def serve_ui():
    """Serves the static index.html file."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")

# --------------------------
# WebSocket: Chat & DAG Updates
# --------------------------

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for chat & DAG-based API execution."""
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        await websocket.send_json({"message": "Welcome! Modify the DAG or type commands like 'List APIs'."})

        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            user_input = data.get("user_input", "").lower()

            # Handle DAG sequence confirmation
            if action == "confirm_sequence":
                global dag_sequence
                dag_sequence = data.get("sequence", [])
                await websocket.send_json({"message": f"Sequence confirmed: {dag_sequence}"})

            # List available APIs
            elif "list" in user_input:
                await websocket.send_json({"message": f"Available APIs: {list(api_map.keys())}"})

            # Execute user-modified sequence using LangGraph
            elif action == "start_execution":
                if not dag_sequence:
                    await websocket.send_json({"message": "No sequence selected! Modify the DAG first."})
                    continue

                await websocket.send_json({"message": f"Executing DAG sequence: {dag_sequence}"})

                # Run the LangGraph-based execution
                results = await workflow_manager.execute_workflow(dag_sequence)

                # Send execution results
                for api, result in results.items():
                    await websocket.send_json({
                        "api": api,
                        "status": result.get("status_code", "Unknown"),
                        "time": result.get("execution_time", 0)
                    })

                await websocket.send_json({"message": "✅ Execution Completed!"})

            # Fetch current DAG structure
            elif action == "get_graph":
                await websocket.send_json({"graph": visualizer.get_execution_graph_json()})

            else:
                await websocket.send_json({"message": "Unknown command. Try 'List APIs' or modify the DAG."})

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected.")
    finally:
        connected_clients.remove(websocket)

# --------------------------
# Run the Application
# --------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
