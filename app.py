"""Week 4 final: deployable chatbot with context control and safe errors."""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from conversation import build_context, messages_to_summarize
from error_policy import AppConfigError, friendly_error
from llm_backend import stream_reply, summarize_messages

load_dotenv(Path(__file__).resolve().parent / ".env")
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

st.set_page_config(page_title="AI Tutor · Week 4 Final", page_icon="🤖")
st.title("Reliable AI Assistant")
st.caption("Week 4 portfolio project · Streaming, memory, API reliability")

DEFAULTS = {
    "messages": [],
    "summary": "",
    "summarized_through": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "last_failed_prompt": None,
}
for name, value in DEFAULTS.items():
    if name not in st.session_state:
        st.session_state[name] = value.copy() if isinstance(value, list) else value


def add_usage(usage):
    """Accumulate usage reported by successful API responses."""
    if usage is not None:
        st.session_state.input_tokens += usage.input_tokens
        st.session_state.output_tokens += usage.output_tokens


with st.sidebar:
    st.subheader("Conversation settings")
    strategy = st.radio("Context strategy", ["Recent only", "Summary + recent"])
    st.write(f"Displayed messages: {len(st.session_state.messages)}")
    st.write(f"Input tokens: {st.session_state.input_tokens}")
    st.write(f"Output tokens: {st.session_state.output_tokens}")
    st.caption("Counters are local to this session and exclude incomplete calls; check API dashboard for billed usage.")
    if st.button("Clear conversation", use_container_width=True):
        for name, value in DEFAULTS.items():
            st.session_state[name] = value.copy() if isinstance(value, list) else value
        st.rerun()
    if strategy == "Summary + recent" and st.session_state.summary:
        with st.expander("Earlier conversation summary"):
            st.write(st.session_state.summary)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

retry = False
if st.session_state.last_failed_prompt:
    st.info("Your previous request failed. Its text wasn't saved to the conversation.")
    retry = st.button("Retry the last failed question")

prompt = st.chat_input("Ask a question")
if retry:
    prompt = st.session_state.last_failed_prompt

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            if not os.getenv("OPENAI_API_KEY"):
                raise AppConfigError("Missing API key")

            # The SDK handles retryable errors before the stream starts.
            client = OpenAI(timeout=45.0, max_retries=2)
            effective_strategy = strategy

            if strategy == "Summary + recent":
                archive = messages_to_summarize(
                    st.session_state.messages, st.session_state.summarized_through
                )
                if archive:
                    try:
                        summary, usage = summarize_messages(
                            client, MODEL, st.session_state.summary, archive
                        )
                    except (OpenAIError, RuntimeError) as exc:
                        st.warning("Summary unavailable. Using recent messages for this reply.")
                        effective_strategy = "Recent only"
                    else:
                        st.session_state.summary = summary
                        st.session_state.summarized_through += len(archive)
                        add_usage(usage)

            messages = build_context(
                st.session_state.messages,
                prompt,
                effective_strategy,
                st.session_state.summary,
                st.session_state.summarized_through,
            )

            tracker = {}
            answer = st.write_stream(stream_reply(client, MODEL, messages, tracker))
            if not tracker.get("completed") or not isinstance(answer, str) or not answer.strip():
                raise RuntimeError("No complete text answer")

        except (OpenAIError, RuntimeError) as exc:
            st.error(friendly_error(exc))
            st.session_state.last_failed_prompt = prompt
            st.caption("If partial text appeared, it will not enter conversation history.")
        else:
            st.session_state.messages.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer},
            ])
            st.session_state.last_failed_prompt = None
            add_usage(tracker.get("usage"))
