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

    def generate_sequence(self, api_map):
        """Generate API execution order using LLM and RunnableSequence."""
        prompt = PromptTemplate(
            template="""
            Given the following OpenAPI endpoints, determine the correct execution order.
            Always return JSON in this format:
            {{
                "execution_order": ["POST /pet", "GET /pet/{petId}", "PUT /pet", "DELETE /pet/{petId}"]
            }}

            Endpoints:
            {api_list}
            """,
            input_variables=["api_list"]
        )

        api_list = "\n".join(api_map.keys())

        sequence = (
            RunnablePassthrough()
            | RunnableLambda(lambda _: {"api_list": api_list})
            | prompt
            | self.llm
            | RunnableLambda(lambda response: json.loads(response.content).get("execution_order", []))
        )

        return sequence.invoke({})  # Return ordered API list

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
