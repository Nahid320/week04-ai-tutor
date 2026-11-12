"""Pure conversation management: independent from Streamlit and the API."""

import json

RECENT_MESSAGES = 6             # Three complete user + assistant turns
SUMMARY_TRIGGER = 12           # Summarize after six complete unsummarized turns


def messages_to_summarize(history, summarized_through):
    """Return older messages to archive while leaving recent turns untouched."""
    unsummarized = history[summarized_through:]
    if len(unsummarized) < SUMMARY_TRIGGER:
        return []
    return unsummarized[:-RECENT_MESSAGES]


def build_context(history, new_question, strategy, summary, summarized_through):
    """Build compact, ordered API input messages."""
    if strategy == "Summary + recent":
        recent = history[summarized_through:]  # Include all unsummarized turns until summarization
        context = []
        if summary:
            context.append({
                "role": "user",
                "content": "Summary of earlier chat (context, not a new request):\n" + summary,
            })
    elif strategy == "Recent only":
        recent = history[-RECENT_MESSAGES:]
        context = []
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return context + recent + [{"role": "user", "content": new_question}]


def make_summary_input(previous_summary, messages):
    """Represent old context explicitly as data for the summarizer."""
    return (
        "Previous summary:\n"
        + (previous_summary or "(none)")
        + "\n\nOlder messages to incorporate:\n"
        + json.dumps(messages, ensure_ascii=False)
    )
