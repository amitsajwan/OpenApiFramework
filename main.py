import uvicorn
from fastapi import FastAPI, WebSocket
from openapi_parser import OpenAPIParser
from llm_sequence_generator import LlmSequenceGenerator
from utils.result_storage import ResultStorage

app = FastAPI()

# Azure OpenAI credentials (Replace with actual values)
AZURE_DEPLOYMENT_NAME = "your-deployment-name"
AZURE_API_BASE = "https://your-endpoint.openai.azure.com/"
AZURE_API_KEY = "your-subscription-key"

# Initialize components
openapi_parser = OpenAPIParser("openapi_specs/petstore.yaml")
llm_generator = LlmSequenceGenerator(
    deployment_name=AZURE_DEPLOYMENT_NAME,
    api_base=AZURE_API_BASE,
    api_key=AZURE_API_KEY
)
result_storage = ResultStorage()  # Tracks execution results & created IDs

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket-based chatbot for real-time API execution updates."""
    await websocket.accept()
    await websocket.send_text("🟢 Chatbot started! Send 'start' to load OpenAPI & execute APIs.")

    while True:
        data = await websocket.receive_text()

        if data.lower() == "start":
            await websocket.send_text("📂 Loading OpenAPI spec...")
            api_endpoints = openapi_parser.get_all_endpoints()

            await websocket.send_text(f"✅ Extracted {len(api_endpoints)} endpoints. Determining execution order...")
            execution_order = llm_generator.generate_api_sequence(api_endpoints)

            response = "\n✅ API Execution Sequence:\n" + "\n".join(f"{i+1}. {ep}" for i, ep in enumerate(execution_order))
            await websocket.send_text(response)

            # Store results for later reporting
            result_storage.save_execution_order(execution_order)

        elif data.lower() == "results":
            results = result_storage.get_execution_results()
            await websocket.send_text(f"📊 Stored Execution Results:\n{results}")

        else:
            await websocket.send_text("⚠️ Unknown command! Send 'start' to begin or 'results' to see past executions.")

# Run FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
