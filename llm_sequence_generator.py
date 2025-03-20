from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json

class LLMSequenceGenerator:
    def __init__(self, model_name="gpt-4-turbo"):
        """Initialize LLM with structured response enforcement."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)

    def generate_execution_order(self, api_map):
        """Determine API execution order using LLM."""
        api_list = list(api_map.keys())  # Extract API keys

        # Define structured prompt for LLM
        prompt = f"""
        You are an API test execution planner. Given the following API endpoints, determine the correct execution order.
        Consider dependencies (e.g., `POST` should run before `GET`, `DELETE` should be last). 

        APIs: {api_list}

        Provide the response **only** as a structured JSON list, like:
        {{"execution_order": ["POST /users", "GET /users", "DELETE /users"]}}
        """

        response = self.llm.invoke([SystemMessage(content="Plan API execution"), HumanMessage(content=prompt)])
        
        try:
            execution_order = json.loads(response.content)["execution_order"]
            return execution_order
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Invalid LLM response format. Ensure JSON structure.")

# Usage example
if __name__ == "__main__":
    sample_api_map = {
        "POST /pet": {},
        "GET /pet/{petId}": {},
        "PUT /pet": {},
        "DELETE /pet/{petId}": {},
        "GET /store/inventory": {}
    }

    generator = LLMSequenceGenerator()
    order = generator.generate_execution_order(sample_api_map)
    print("Execution Order:", order)
  
