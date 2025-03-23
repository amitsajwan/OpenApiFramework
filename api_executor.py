import aiohttp
import asyncio
import logging

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)

class APIExecutor:
    def __init__(self, base_url, headers=None, max_retries=3, timeout=10):
        """
        Initialize the API executor with a base URL, optional headers, and retry logic.
        
        :param base_url: Base API URL
        :param headers: Default headers for all requests
        :param max_retries: Maximum retry attempts for failed requests
        :param timeout: Timeout for API requests (in seconds)
        """
        self.base_url = base_url
        self.headers = headers if headers else {}
        self.max_retries = max_retries
        self.timeout = timeout

    async def execute_api(self, method, endpoint, payload=None):
        """
        Execute an API request asynchronously with retry logic.
        
        :param method: HTTP method (GET, POST, PUT, DELETE)
        :param endpoint: API endpoint (e.g., /pet)
        :param payload: Request payload (if applicable)
        :return: Dictionary containing status code and response
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0

        while attempt < self.max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method, url, json=payload, headers=self.headers, timeout=self.timeout
                    ) as response:
                        return {
                            "api": f"{method} {endpoint}",
                            "status_code": response.status,
                            "response": await response.text()
                        }
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {str(e)}")
                attempt += 1
                await asyncio.sleep(2)  # Wait before retrying

        logging.error(f"API request failed after {self.max_retries} retries: {url}")
        return {
            "api": f"{method} {endpoint}",
            "status_code": "ERROR",
            "response": f"Failed after {self.max_retries} retries"
        }

    async def execute_multiple_apis(self, api_requests):
        """
        Execute multiple API requests asynchronously in parallel.
        
        :param api_requests: List of dictionaries with "method", "endpoint", and optional "payload"
        :return: List of API responses
        """
        tasks = [
            self.execute_api(api["method"], api["endpoint"], api.get("payload"))
            for api in api_requests
        ]
        return await asyncio.gather(*tasks)

# Example usage
if __name__ == "__main__":
    async def main():
        executor = APIExecutor(base_url="https://petstore.swagger.io/v2", max_retries=3, timeout=5)

        # Single API call example
        result = await executor.execute_api("GET", "/pet/findByStatus?status=available")
        print(result)

        # Multiple API calls in parallel
        requests = [
            {"method": "GET", "endpoint": "/pet/1"},
            {"method": "GET", "endpoint": "/store/inventory"}
        ]
        results = await executor.execute_multiple_apis(requests)
        print(results)

    asyncio.run(main())
