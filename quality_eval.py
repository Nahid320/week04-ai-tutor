"""Small, reproducible, narrow smoke checks for short factual answers.

Exact-match on constrained questions is NOT a broad measure of chatbot quality.
"""

import re


def normalize_answer(value: str) -> str:
    """Remove harmless surrounding whitespace, case, and punctuation."""
    cleaned = value.strip().casefold()
    cleaned = re.sub(r"^[\s\W_]+|[\s\W_]+$", "", cleaned)
    return cleaned


def score_answer(answer: str, expected: str) -> bool:
    return normalize_answer(answer) == normalize_answer(expected)


def summarize_scores(results: list[dict]) -> dict:
    """Failures count as incorrect; never silently omit failed API calls."""
    total = len(results)
    completed = sum(x["completed"] for x in results)
    correct = sum(x["correct"] for x in results)
    input_tokens = sum(x.get("input_tokens", 0) for x in results)
    output_tokens = sum(x.get("output_tokens", 0) for x in results)
    return {
        "total": total,
        "completed": completed,
        "correct": correct,
        "completion_rate": (completed / total if total else 0.0),
        "exact_match_accuracy": (correct / total if total else 0.0),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
