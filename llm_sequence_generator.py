import json
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class LlmSequenceGenerator:
    """Generates API execution sequence using Azure OpenAI."""

    def __init__(self, deployment_name, api_base, api_key, api_version="2023-03-15-preview"):
        """Initialize Azure OpenAI with the provided credentials."""
        self.llm = AzureChatOpenAI(
            deployment_name=deployment_name,
            openai_api_base=api_base,
            openai_api_key=api_key,
            openai_api_version=api_version
        )

        # Define a structured JSON prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["api_endpoints"],
            template="""
            Given the following API endpoints: {api_endpoints}, determine the correct execution order.
            Ensure the response is in **strict JSON format**:
            ```json
            {{"execution_order": ["POST /pet", "GET /pet/{petId}", "PUT /pet", "DELETE /pet/{petId}"]}}
            ```
            """
        )

    def generate_api_sequence(self, api_endpoints):
        """Uses Azure OpenAI to determine the correct API execution sequence."""
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        response = chain.run({"api_endpoints": api_endpoints})
        
        try:
            sequence = json.loads(response)["execution_order"]
        except json.JSONDecodeError:
            print("⚠️ Error: LLM did not return valid JSON. Using default order.")
            sequence = api_endpoints  # Fallback to provided order

        return sequence
