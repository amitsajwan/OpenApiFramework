import json
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Azure OpenAI
llm = AzureChatOpenAI(
    deployment_name="your-deployment-name",  # Found in Azure portal
    openai_api_base="https://your-endpoint.openai.azure.com/",
    openai_api_key="your-subscription-key",
    openai_api_version="2023-03-15-preview"
)

# Define a prompt template ensuring JSON output
prompt_template = PromptTemplate(
    input_variables=["api_endpoints"],
    template="""
    Given the following API endpoints: {api_endpoints}, determine the correct execution order.
    Ensure the response is in **strict JSON format**:
    ```json
    {{"execution_order": ["POST /pet", "GET /pet/{petId}", "PUT /pet", "DELETE /pet/{petId}"]}}
    ```
    """
)

def generate_api_sequence(api_endpoints):
    """Uses Azure OpenAI to determine the correct API execution sequence."""
    
    chain = LLMChain(llm=llm, prompt=prompt_template)

    response = chain.run({"api_endpoints": api_endpoints})
    
    try:
        sequence = json.loads(response)["execution_order"]
    except json.JSONDecodeError:
        print("⚠️ Error: LLM did not return valid JSON. Using default order.")
        sequence = api_endpoints  # Fallback to the provided order

    return sequence
