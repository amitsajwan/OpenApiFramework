from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import json

app = FastAPI()
clients = []

@app.get("/")
async def get():
    """Serve a simple chatbot UI."""
    return HTMLResponse("""
    <html>
    <head>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var log = document.getElementById("log");
                log.innerHTML += event.data + "<br>";
            };
            function sendMessage() {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = "";
            }
        </script>
    </head>
    <body>
        <h2>API Test Execution</h2>
        <div id="log"></div>
        <input id="messageText" type="text">
        <button onclick="sendMessage()">Send</button>
    </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle real-time chatbot updates."""
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(f"User: {data}")
    except:
        clients.remove(websocket)

async def broadcast(message):
    """Send messages to all connected clients."""
    for client in clients:
        await client.send_text(message)

async def send_execution_update(api_key, status, time_taken):
    """Send execution updates to the chatbot UI."""
    message = f"Executed {api_key} → Status: {status}, Time: {time_taken}s"
    await broadcast(message)
