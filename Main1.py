from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# Serve static files (for index.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("🔹 Welcome to the API Testing Chatbot! 🔹")
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"🤖 Echo: {data}")  # Placeholder for chatbot logic

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
