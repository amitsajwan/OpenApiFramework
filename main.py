from fastapi import FastAPI, WebSocket
import json

app = FastAPI()

# WebSocket endpoint for chatbot UI updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"message": "Connected to API Testing Bot"}))
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(json.dumps({"message": f"Received: {data}"})))
