import unittest
from types import SimpleNamespace

from llm_backend import stream_reply


def evt(kind, **kwargs):
    return SimpleNamespace(type=kind, **kwargs)


class StreamContext:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return iter(self.events)

    def __exit__(self, *args):
        return False


class FakeResponses:
    def __init__(self, events):
        self.events = events
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return StreamContext(self.events)


class StreamingTests(unittest.TestCase):
    def test_deltas_and_completion_record_usage(self):
        usage = SimpleNamespace(input_tokens=10, output_tokens=2)
        fake = FakeResponses([
            evt("response.output_text.delta", delta="Hello"),
            evt("response.output_text.delta", delta=" world"),
            evt("response.completed", response=SimpleNamespace(usage=usage)),
        ])
        client = SimpleNamespace(responses=fake)
        tracker = {}
        answer = "".join(stream_reply(client, "example-model", [{"role":"user", "content":"hi"}], tracker))
        self.assertEqual(answer, "Hello world")
        self.assertTrue(tracker["completed"])
        self.assertIs(tracker["usage"], usage)
        self.assertTrue(fake.request["stream"])
        self.assertFalse(fake.request["store"])

    def test_incomplete_stream_raises(self):
        client = SimpleNamespace(responses=FakeResponses([
            evt("response.output_text.delta", delta="partial")
        ]))
        with self.assertRaisesRegex(RuntimeError, "without a response.completed"):
            list(stream_reply(client, "m", [{"role":"user", "content":"hi"}], {}))

    def test_failed_stream_raises(self):
        client = SimpleNamespace(responses=FakeResponses([
            evt("response.failed")
        ]))
        with self.assertRaisesRegex(RuntimeError, "response.failed"):
            list(stream_reply(client, "m", [], {}))


if __name__ == "__main__":
    unittest.main()
