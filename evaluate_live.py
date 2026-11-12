"""Run a small benchmark using live API calls (optional; incurs API costs).

Usage: python evaluate_live.py
"""

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from error_policy import friendly_error
from quality_eval import score_answer, summarize_scores

ROOT = Path(__file__).resolve().parent


def run_evaluation(client, model: str, cases: list[dict]) -> dict:
    rows = []
    for case in cases:
        start = time.perf_counter()
        row = {
            "id": case["id"],
            "expected": case["expected"],
            "completed": False,
            "correct": False,
            "answer": None,
            "error": None,
            "input_tokens": 0,
            "output_tokens": 0,
        }
        try:
            response = client.responses.create(
                model=model,
                instructions=(
                    "Answer the factual question accurately. "
                    "Follow the requested short answer format."
                ),
                input=case["prompt"],
                reasoning={"effort": "none"},
                max_output_tokens=80,
                store=False,
            )
            if response.status != "completed" or not response.output_text.strip():
                raise RuntimeError("Incomplete response")
            row["answer"] = response.output_text.strip()
            row["completed"] = True
            row["correct"] = score_answer(row["answer"], case["expected"])
            if response.usage is not None:
                row["input_tokens"] = response.usage.input_tokens
                row["output_tokens"] = response.usage.output_tokens
        except Exception as error:
            # In this educational test runner, capture safe public messages only.
            row["error"] = friendly_error(error)
        row["latency_seconds"] = round(time.perf_counter() - start, 3)
        rows.append(row)
    return {
        "model": model,
        "metrics": summarize_scores(rows),
        "results": rows,
        "note": "Exact-match smoke test on six constrained questions, not a comprehensive evaluation."
    }


def main():
    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY in .env")
    from openai import OpenAI

    model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
    cases = json.loads((ROOT / "eval_cases.json").read_text(encoding="utf-8"))
    # Automatic SDK retries: only temporary errors. No manual retry loop.
    client = OpenAI(timeout=45.0, max_retries=2)
    report = run_evaluation(client, model, cases)
    output = ROOT / "outputs" / "smoke_test_report.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["metrics"], indent=2))
    print("Saved:", output)
    print("Review individual answers; exact matching misses valid paraphrases.")


if __name__ == "__main__":
    main()
