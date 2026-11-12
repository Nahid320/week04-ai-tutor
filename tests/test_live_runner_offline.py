import unittest
from types import SimpleNamespace
from evaluate_live import run_evaluation

class FakeResponses:
    def __init__(self, responses):
        self._responses = iter(responses)
    def create(self, **kwargs):
        value = next(self._responses)
        if isinstance(value, Exception):
            raise value
        return value

def resp(text, status="completed", input_tokens=8, output_tokens=2):
    return SimpleNamespace(
        status=status,
        output_text=text,
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )

class RunnerTests(unittest.TestCase):
    def test_mix_of_valid_wrong_and_failure(self):
        client = SimpleNamespace(responses=FakeResponses([
            resp("56"), resp("wrong"), RuntimeError("failed"),
        ]))
        cases = [
            {"id":"one", "prompt":"q1", "expected":"56"},
            {"id":"two", "prompt":"q2", "expected":"softmax"},
            {"id":"three", "prompt":"q3", "expected":"precision"},
        ]
        report = run_evaluation(client,"test-model", cases)
        self.assertEqual(report["metrics"]["correct"], 1)
        self.assertEqual(report["metrics"]["completed"], 2)
        self.assertEqual(report["metrics"]["total"], 3)
        self.assertEqual(report["metrics"]["input_tokens"], 16)
        self.assertIsNotNone(report["results"][-1]["error"])

    def test_empty_answer_is_not_completed(self):
        client = SimpleNamespace(responses=FakeResponses([resp("",status="completed")]))
        report = run_evaluation(client,"test-model", [{"id":"x","prompt":"q","expected":"y"}])
        self.assertEqual(report["metrics"]["completed"], 0)

if __name__ == "__main__":
    unittest.main()
