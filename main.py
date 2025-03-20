import yaml
import asyncio
from api_executor import APIExecutor
from api_workflow import APIWorkflow
from chatbot_ui import send_execution_update
from openapi_parser import extract_openapi_details
from llm_sequence_generator import generate_api_execution_order

async def main():
    # Load OpenAPI spec
    openapi_file = input("Enter OpenAPI YAML file path: ")
    with open(openapi_file, "r") as f:
        openapi_spec = yaml.safe_load(f)

    # Extract API details
    base_url, headers, api_map = extract_openapi_details(openapi_spec)

    # Ask user for additional headers
    user_headers = input("Enter any additional headers (API key, cookies) as JSON: ")
    if user_headers:
        headers.update(yaml.safe_load(user_headers))

    # Generate API execution sequence
    execution_sequence = generate_api_execution_order(api_map)

    # Initialize API Executor
    api_executor = APIExecutor(base_url, headers, api_map)

    # Setup workflow
    workflow = APIWorkflow(api_executor, execution_sequence)
    workflow.build_workflow()

    # Execute workflow & update chatbot
    print("\nStarting API Execution...\n")
    results = workflow.run()

    # Send execution updates to chatbot UI
    for api_key, result in results.items():
        await send_execution_update(api_key, result["status_code"], result["response_time"])

    # Ask for load testing
    run_load_test = input("Do you want to run a load test? (yes/no): ").strip().lower()
    if run_load_test == "yes":
        num_users = int(input("Enter number of users: "))
        print(f"\nRunning load test with {num_users} users...\n")
        await asyncio.gather(*[workflow.run() for _ in range(num_users)])

if __name__ == "__main__":
    asyncio.run(main())
