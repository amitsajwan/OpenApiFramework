# LangGraph-Based Automated API Testing Framework

## Overview
This framework automates API testing using OpenAPI specifications. It determines execution order intelligently, supports asynchronous workflows, and includes chatbot-based human intervention for critical steps.

## How It Works

### 1️⃣ Load OpenAPI YAML
When you run the framework, it prompts you to select an OpenAPI spec from the `openapi_specs/` folder.

### 2️⃣ Extract API Endpoints & Schemas
The framework parses the selected OpenAPI YAML file and extracts:
- API endpoints (paths, methods)
- Request/response schemas
- Base URL, headers, and authentication details

### 3️⃣ Determine API Execution Order
An LLM is used to determine the correct sequence of API execution, ensuring dependencies (e.g., creating before retrieving).

### 4️⃣ Generate Example Payloads
For `POST` and `PUT` requests, the framework automatically generates example payloads by resolving `$ref` references, enums, and nested schemas.

### 5️⃣ Build LangGraph Workflow
Each API endpoint is added as a **node** in the LangGraph workflow. Edges define the execution order.

### 6️⃣ Execute APIs (Sequential & Parallel)
- APIs execute in order, either **sequentially** or **asynchronously in parallel**, when applicable.
- The chatbot UI displays real-time execution progress.

### 7️⃣ Human-in-the-Loop (Optional)
For critical API steps, the chatbot asks for confirmation before proceeding.

### 8️⃣ Store Results & Created IDs
- Execution results (success/failure, response time) are stored for reporting.
- Created IDs (e.g., user ID, order ID) are saved for later use (e.g., DELETE requests).

### 9️⃣ Run Load Tests (Optional)
After the first test run, the chatbot asks if you want to:
- **Re-run the test** or
- **Run a load test** with a specified number of users

## Installation

```bash
git clone <repository-url>
cd api_testing_framework
pip install -r requirements.txt
```

## Running the Framework

```bash
python api_testing_framework/main.py
```

## Configuration

- Place OpenAPI YAML files in the `openapi_specs/` folder.
- The framework will ask for the base URL and any required headers (API keys, cookies, etc.).

## Features

✔️ **OpenAPI Parsing** – Extracts API details automatically  
✔️ **Smart Execution Order** – Uses LLM to determine API sequence  
✔️ **Payload Generation** – Resolves `$ref`, enums, and nested schemas  
✔️ **Asynchronous Execution** – Runs APIs sequentially or in parallel  
✔️ **Human-in-the-Loop** – Prompts user for critical steps  
✔️ **Real-time Chatbot UI** – Displays progress updates  
✔️ **Load Testing Support** – Simulate multiple users  
✔️ **Result Storage** – Saves execution logs and created IDs  

## Example Execution Output

```plaintext
🔍 Loading OpenAPI Spec: petstore.yaml

🔗 Extracted Endpoints:
- POST /pet
- GET /pet/{petId}
- PUT /pet
- DELETE /pet/{petId}
- GET /store/inventory

📌 Execution Sequence:
1. POST /pet
2. GET /pet/{petId}
3. PUT /pet
4. DELETE /pet/{petId}
5. GET /store/inventory

🚀 Running API Tests...
✅ POST /pet - 200 OK (Time: 120ms)
✅ GET /pet/{petId} - 200 OK (Time: 85ms)
✅ PUT /pet - 200 OK (Time: 100ms)
✅ DELETE /pet/{petId} - 204 No Content (Time: 95ms)
✅ GET /store/inventory - 200 OK (Time: 70ms)

🎯 Test Run Completed Successfully
```

## Contributing

Feel free to contribute by submitting PRs or opening issues.

---
