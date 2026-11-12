import unittest
from error_policy import AppConfigError, friendly_error

class FakeStatusError(Exception):
    def __init__(self, status):
        self.status_code = status

class APIConnectionError(Exception):
    pass

class APITimeoutError(Exception):
    pass

class ErrorPolicyTests(unittest.TestCase):
    def test_missing_config(self):
        self.assertIn("OPENAI_API_KEY", friendly_error(AppConfigError("Missing API key")))

    def test_invalid_key(self):
        self.assertIn("OPENAI_API_KEY", friendly_error(FakeStatusError(401)))

    def test_quota_or_rate_limit(self):
        self.assertIn("429", friendly_error(FakeStatusError(429)))

    def test_server_issue(self):
        self.assertIn("Temporary", friendly_error(FakeStatusError(503)))

    def test_bad_request(self):
        self.assertIn("Request rejected", friendly_error(FakeStatusError(400)))

    def test_timeout(self):
        self.assertIn("timeout", friendly_error(APITimeoutError()).lower())

    def test_connection(self):
        self.assertIn("Connection", friendly_error(APIConnectionError()))

    def test_unknown_error_does_not_expose_secret(self):
        self.assertNotIn("topsecret", friendly_error(Exception("topsecret")))

    def test_runtime_error(self):
        self.assertIn("incomplete", friendly_error(RuntimeError("failed")))

if __name__ == "__main__":
    unittest.main()
