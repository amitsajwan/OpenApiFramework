import unittest
from api_workflow import APIWorkflow
from api_executor import APIExecutor

class TestAPIWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up API workflow with mock data."""
        self.executor = APIExecutor()
        self.workflow = APIWorkflow(self.executor, ["GET /test", "POST /submit"])

    def test_execute_valid_api(self):
        """Ensure valid API execution returns expected results."""
        result = self.workflow.execute_api("GET /test")
        self.assertIn("status_code", result)

    def test_execute_invalid_api(self):
        """Ensure invalid API calls return an error."""
        result = self.workflow.execute_api("INVALID /unknown")
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
