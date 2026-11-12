import unittest

from conversation import build_context, messages_to_summarize, make_summary_input


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"text-{i}"}
            for i in range(14)
        ]

    def test_recent_only_uses_six_messages_and_new_question(self):
        context = build_context(self.history, "next", "Recent only", "", 0)
        self.assertEqual(len(context), 7)
        self.assertEqual(context[0]["content"], "text-8")
        self.assertEqual(context[-1]["content"], "next")

    def test_summary_included_as_historical_context(self):
        context = build_context(self.history, "next", "Summary + recent", "Earlier detail", 6)
        self.assertEqual(len(context), 10)
        self.assertIn("Earlier detail", context[0]["content"])
        self.assertEqual(context[1]["content"], "text-6")

    def test_no_missing_unsummarized_messages_before_threshold(self):
        context = build_context(self.history[:10], "next", "Summary + recent", "", 0)
        self.assertEqual(len(context), 11)
        self.assertEqual(context[0]["content"], "text-0")

    def test_archive_only_old_messages(self):
        archive = messages_to_summarize(self.history, 0)
        self.assertEqual([x["content"] for x in archive], [f"text-{i}" for i in range(8)])

    def test_archive_threshold(self):
        self.assertEqual(messages_to_summarize(self.history[:10], 0), [])
        self.assertEqual(len(messages_to_summarize(self.history[:12], 0)), 6)

    def test_summary_pointer_respected(self):
        archive = messages_to_summarize(self.history, 6)
        self.assertEqual(archive, [])

    def test_summary_payload_contains_history(self):
        text = make_summary_input("old", self.history[:2])
        self.assertIn("old", text)
        self.assertIn("text-1", text)

    def test_unknown_strategy_rejected(self):
        with self.assertRaises(ValueError):
            build_context([], "hi", "unknown", "", 0)


if __name__ == "__main__":
    unittest.main()
