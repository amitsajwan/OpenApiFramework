# LangGraph API Testing Framework

## Features
- Automated API execution using OpenAPI spec.
- Execution sequence determined by LLM.
- WebSocket-based chatbot UI for real-time execution updates.
- Human-in-the-loop intervention for critical steps.
- Memory tracking for execution results and created IDs.
- Asynchronous execution with LangGraph.
- Load testing support.

## Installation
```sh
pip install -r requirements.txt
```

## Running the Server
```sh
uvicorn api.main:app --reload
```

## Using the Chatbot UI
Open `ui/chatbot_ui.html` in your browser.

## Running Tests
```sh
pytest tests/
```