from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def get():
    """Serve a simple chatbot UI with Bootstrap styling."""
    return HTMLResponse("""
    <html>
    <head>
        <title>API Workflow Chat</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var log = document.getElementById("log");
                log.innerHTML += "<div class='alert alert-info'>" + event.data + "</div>";
            };
        </script>
    </head>
    <body class="container mt-4">
        <h2 class="text-center">API Workflow Chat</h2>
        <div id="log" class="border p-3" style="height: 300px; overflow-y: auto;"></div>
    </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected!")
