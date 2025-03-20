import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Import our modules
from openapi_parser import OpenAPIParser
from llm_sequence_generator import LLMSequenceGenerator
from api_executor import ApiExecutor
from utils.result_storage import ResultStorage

# Create FastAPI app and enable CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances for OpenAPI parsing and result storage
openapi_parser = OpenAPIParser("openapi_specs/petstore.yaml")
result_storage = ResultStorage()

# Azure OpenAI configuration (update with your values)
AZURE_ENDPOINT = "https://your-azure-endpoint.openai.azure.com/"
AZURE_KEY = "your-azure-key"
DEPLOYMENT_NAME = "your-deployment-name"

# Initialize LLM sequence generator
llm_sequence_generator = LLMSequenceGenerator(
    azure_endpoint=AZURE_ENDPOINT,
    azure_key=AZURE_KEY,
    deployment_name=DEPLOYMENT_NAME
)

@app.get("/")
async def serve_index():
    """Serve the index HTML page."""
    return FileResponse("static/index.html")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chatbot interaction."""
    await websocket.accept()
    try:
        await websocket.send_text("🔹 Welcome to the API Testing Chatbot!")
        await websocket.send_text("Please enter the API Base URL (e.g., https://petstore.example.com):")
        base_url = await websocket.receive_text()
        
        await websocket.send_text("Enter any required headers as JSON (or type 'skip'):")
        headers_input = await websocket.receive_text()
        headers = {} if headers_input.lower() == "skip" else eval(headers_input)  # Use safe parsing in production

        # Extract API endpoints from OpenAPI YAML using our parser
        api_map = openapi_parser.get_all_endpoints()
        if not api_map:
            await websocket.send_text("⚠️ No API endpoints found in the OpenAPI spec. Exiting.")
            return
        await websocket.send_text(f"✅ Extracted {len(api_map)} endpoints.")

        # Determine API execution order using LLMSequenceGenerator
        execution_order = llm_sequence_generator.generate_sequence(api_map)
        await websocket.send_text("✅ API Execution Order:")
        for idx, ep in enumerate(execution_order, start=1):
            await websocket.send_text(f"{idx}. {ep}")

        # Initialize the APIExecutor with base URL, headers, and Azure config for payload generation
        api_executor = ApiExecutor(base_url, headers, AZURE_ENDPOINT, AZURE_KEY, DEPLOYMENT_NAME)
        
        # Execute API sequence (this method should internally generate payloads for POST/PUT)
        execution_results = api_executor.execute_api_sequence(api_map)
        
        # Store the results for reporting
        result_storage.save_results(execution_results)
        
        # Send the final results back to the chatbot UI
        await websocket.send_text("📊 Execution Completed. Results:")
        await websocket.send_text(str(execution_results))
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

if __name__ == "__main__":
    # Use an import string so that uvicorn can reload properly:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
