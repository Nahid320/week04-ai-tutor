import unittest
from quality_eval import normalize_answer, score_answer, summarize_scores

class EvaluationTests(unittest.TestCase):
    def test_whitespace_and_case(self):
        self.assertTrue(score_answer(" SOFTMAX. ", "softmax"))

    def test_wrong_answer(self):
        self.assertFalse(score_answer("recall", "precision"))

    def test_normalization_no_loss_of_internal_characters(self):
        self.assertEqual(normalize_answer("  42! "), "42")

    def test_error_counts_in_denominator(self):
        rows = [
            {"completed": True, "correct": True, "input_tokens": 10, "output_tokens": 2},
            {"completed": True, "correct": False, "input_tokens": 10, "output_tokens": 2},
            {"completed": False, "correct": False},
        ]
        report = summarize_scores(rows)
        self.assertAlmostEqual(report["completion_rate"], 2/3)
        self.assertAlmostEqual(report["exact_match_accuracy"], 1/3)
        self.assertEqual(report["input_tokens"], 20)

    def test_empty_results(self):
        report = summarize_scores([])
        self.assertEqual(report["exact_match_accuracy"], 0.0)

if __name__ == "__main__":
    unittest.main()
