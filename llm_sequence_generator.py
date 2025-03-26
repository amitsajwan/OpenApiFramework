import json
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableSequence
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate

class LLMSequenceGenerator:
    def __init__(self, azure_endpoint: str, azure_key: str, deployment_name: str):
        """Initialize Azure OpenAI chat model."""
        self.llm = AzureChatOpenAI(
            openai_api_base=azure_endpoint,
            openai_api_version="2023-03-15-preview",
            deployment_name=deployment_name,
            openai_api_key=azure_key
        )

    def generate_graph(self, api_map):
        """Generate API execution graph (nodes & edges) dynamically."""
        prompt = PromptTemplate(
            template="""
            Given the following OpenAPI endpoints, determine the correct execution order.
    
            Rules:
            - **Identify dependencies:** If an API needs data from another, it must run **after** it.
            - **Parallel execution:** If APIs are independent, they can run **in parallel**.
            - **Always return JSON** with `nodes` (all APIs) and `edges` (execution order).
    
            **Example Output:**
            {{
                "nodes": ["POST /user", "GET /user/{userId}", "GET /users", "DELETE /user/{userId}"],
                "edges": [
                    ["POST /user", "GET /user/{userId}"],
                    ["GET /user/{userId}", "DELETE /user/{userId}"]
                ]
            }}
    
            **OpenAPI Endpoints:**
            {api_list}
            """,
            input_variables=["api_list"]
        )
    
        api_list = "\n".join(api_map.keys())
    
        graph_structure = (
            RunnablePassthrough()
            | RunnableLambda(lambda _: {"api_list": api_list})
            | prompt
            | self.llm
            | RunnableLambda(lambda response: json.loads(response.content))
        )
    
        return graph_structure.invoke({})
    
        
    def generate_payload(self, endpoint_details):
        """Generate a sample JSON payload for POST/PUT requests."""
        prompt = PromptTemplate(
            template="""
            Given the following OpenAPI request schema, generate a sample JSON payload.
            Ensure the response is a valid JSON object.

            Schema:
            {schema}

            Output JSON:
            """,
            input_variables=["schema"]
        )

        schema = json.dumps(endpoint_details, indent=2)  # Convert schema to JSON string

        sequence = (
            RunnablePassthrough()
            | RunnableLambda(lambda _: {"schema": schema})
            | prompt
            | self.llm
            | RunnableLambda(lambda response: json.loads(response.content))
        )

        return sequence.invoke({})
