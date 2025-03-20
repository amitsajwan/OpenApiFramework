from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from openapi_parser import OpenAPIParser
from llm_sequence_generator import LLMSequenceGenerator
from api_executor import APIExecutor
from utils.result_storage import ResultStorage

# Initialize FastAPI app
app = FastAPI()

# Enable CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Global instances
parser = OpenAPIParser("openapi_specs/petstore.yaml")  # Load OpenAPI spec
llm_sequence_generator = LLMSequenceGenerator()
result_storage = ResultStorage()


@app.get("/")
async def home():
    return {"message": "API Testing Chatbot is running! Open http://127.0.0.1:8000/chat in browser."}


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("🔹 Welcome to the API Testing Chatbot! 🔹")
    
    # Get API base URL from user
    await websocket.send_text("Enter API Base URL:")
    base_url = await websocket.receive_text()
    
    # Get headers (optional)
    await websocket.send_text("Enter any required headers as JSON (or type 'skip'):")
    headers_input = await websocket.receive_text()
    headers = eval(headers_input) if headers_input.lower() != "skip" else {}

    # Extract API details from OpenAPI YAML
    api_map = parser.get_all_endpoints()

    if not api_map:
        await websocket.send_text("⚠️ No APIs found in OpenAPI spec. Exiting...")
        return
    
    # Generate API execution sequence using LLM
    api_sequence = llm_sequence_generator.generate_execution_sequence(api_map)

    await websocket.send_text(f"✅ Execution sequence:\n{api_sequence}")

    # Initialize APIExecutor properly
    api_executor = APIExecutor(base_url, headers)

    # Execute APIs in sequence
    execution_results = await api_executor.execute_sequence(api_sequence, api_map)

    # Store results for reporting
    result_storage.save_results(execution_results)

    await websocket.send_text(f"📊 Execution Complete. Summary:\n{execution_results}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    
