import os
import zipfile

def create_zip_from_directory(directory_path, zip_file_path):
    """Creates a zip file from a directory."""
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))

# Create the directory structure in memory (for zip creation)
# You would normally get this from the file system.
file_structure = {
    "src/openapi_genai/config/config.py": """
import os

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # Add other configuration variables here
    # ...
    """,
    "src/openapi_genai/utils/logging.py": """
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    """,
    "src/openapi_genai/agents/base_agent.py": """
from abc import ABC, abstractmethod
from openapi_genai.config.config import Config
import logging

class BaseAgent(ABC):
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def generate_output(self, input_data: dict) -> str:
        \"\"\"Generates output based on the provided input data.\"\"\"
        pass
    """,
    "src/openapi_genai/agents/documentation_agent.py": """
from openapi_genai.agents.base_agent import BaseAgent
import openai

class DocumentationAgent(BaseAgent):
    def generate_output(self, input_data: dict) -> str:
        try:
            openai.api_key = self.config.OPENAI_API_KEY
            # Use input_data and call OpenAI API for documentation
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Generate documentation for API: {input_data}",
                max_tokens=200,
            )
            return response.choices[0].text.strip()
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            return "Error generating documentation."
    """,
    "src/openapi_genai/core/api_processor.py": """
from openapi_genai.agents.base_agent import BaseAgent
import logging

def process_api(openapi_spec: dict, agent: BaseAgent) -> str:
    logger = logging.getLogger(__name__)
    try:
        result = agent.generate_output(openapi_spec)
        return result
    except Exception as e:
        logger.error(f"Error processing API: {e}")
        return "Error processing API."
    """,
    "src/openapi_genai/human_in_loop/feedback.py": """
def get_user_feedback(generated_output: str) -> str:
    feedback = input(f"Review the following output:\\n{generated_output}\\n\\nEnter your feedback (or 'ok' if it's fine): ")
    return feedback
    """,
    "src/openapi_genai/visualizations/graphs.py": """
import matplotlib.pyplot as plt

def generate_api_call_graph(api_data: dict):
    # Example: Create a simple bar chart of API call counts
    call_counts = {}
    for path, methods in api_data["paths"].items():
        for method in methods:
            if method in call_counts:
                call_counts[method] += 1
            else:
                call_counts[method] = 1

    plt.bar(call_counts.keys(), call_counts.values())
    plt.xlabel("API Methods")
    plt.ylabel("Call Count")
    plt.title("API Call Distribution")
    plt.show()
    """,
    "src/openapi_genai/app.py": """
from openapi_genai.agents.documentation_agent import DocumentationAgent
from openapi_genai.core.api_processor import process_api
from openapi_genai.human_in_loop.feedback import get_user_feedback
from openapi_genai.visualizations.graphs import generate_api_call_graph
from openapi_genai.utils.logging import setup_logging
import json

def main():
    setup_logging()
    agent = DocumentationAgent()
    with open("openapi.json", "r") as f:
        openapi_spec = json.load(f)

    generated_docs = process_api(openapi_spec, agent)
    feedback = get_user_feedback(generated_docs)

    if feedback.lower() != "ok":
        print("Feedback received. Updating documentation...")
        # Incorporate feedback into the generated docs.

    generate_api_call_graph(openapi_spec)

if __name__ == "__main__":
    main()
    """,
    "openapi.json": """
{
  "openapi": "3.0.0",
  "info": {
    "title": "Sample API",
    "version": "1.0.0"
  },
  "paths": {
    "/users": {
      "get": {
        "summary": "Get all users",
        "responses": {
          "200": {
            "description": "A list of users"
          }
        }
      },
      "post": {
        "summary": "Create a new user",
        "responses": {
          "201": {
            "description": "User created"
          }
        }
      }
    },
    "/products":{
        "get":{
            "summary": "get all products",
            "responses": {
                "200": {
                    "description": "A list of products"
                }
            }
        }
    }
  }
}
"""
}

# Create a temporary directory structure in memory
temp_dir = "temp_openapi_genai"
os.makedirs(temp_dir, exist_ok=True)
for file_path, content in file_structure.items():
    full_path = os.path.join(temp_dir, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

# Create the zip file
zip_file_path = "openapi_genai.zip"
create_zip_from_directory(temp_dir, zip_file_path)

# Clean up the temporary directory
import shutil
shutil.rmtree(temp_dir)

print(f"Zip file created: {zip_file_path}")
