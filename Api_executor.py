import json
import requests
from llm_sequence_generator import LLMSequenceGenerator

class ApiExecutor:
    def __init__(self, base_url, headers, azure_endpoint, azure_key, deployment_name):
        """
        Initialize API executor with base URL, headers, and LLM for payload generation.
        """
        self.base_url = base_url
        self.headers = headers
        self.sequence_generator = LLMSequenceGenerator(azure_endpoint, azure_key, deployment_name)

    def execute_api_sequence(self, api_map):
        """
        Execute the API sequence determined by LLM.
        """
        execution_order = self.sequence_generator.generate_sequence(api_map)

        for api in execution_order:
            method, path = api.split(" ", 1)
            url = f"{self.base_url}{path}"
            details = api_map.get(api, {})

            # Generate payload for POST/PUT
            payload = None
            if method in ["POST", "PUT"]:
                payload = self.sequence_generator.generate_payload(details.get("requestBody", {}))

            response = self._make_request(method, url, payload)
            print(f"{method} {url} → Status: {response.status_code}, Response: {response.json()}")

    def _make_request(self, method, url, payload=None):
        """
        Make an HTTP request with optional payload.
        """
        try:
            response = requests.request(
                method, url, headers=self.headers, json=payload
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
