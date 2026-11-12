"""Classify API failures into safe, actionable messages. No raw secrets or prompts."""

class AppConfigError(RuntimeError):
    """Missing or invalid application configuration."""


def friendly_error(error: Exception) -> str:
    if isinstance(error, AppConfigError):
        return "OPENAI_API_KEY is missing. Add it to your .env file before running the app."
    status = getattr(error, "status_code", None)
    if status == 401:
        return "Authentication failed (401). Check OPENAI_API_KEY in .env."
    if status == 403:
        return "Access denied (403). Check project permissions and model access."
    if status == 429:
        return (
            "Rate limit or quota error (429). Check API usage and billing. "
            "Retry later only if this is a temporary rate limit."
        )
    if status in (400, 404, 422):
        return "Request rejected. Check model ID, parameters, and SDK version."
    if status in (408, 409) or (isinstance(status, int) and status >= 500):
        return "Temporary API issue. Automatic retries may already have been attempted."
    if type(error).__name__ in {"APIConnectionError", "APITimeoutError"}:
        return "Connection or timeout problem. Check network access and try again."
    if isinstance(error, RuntimeError):
        return "The response was incomplete or interrupted. It was not saved to chat history."
    return "The request failed. Check your network, API access, or application logs."
