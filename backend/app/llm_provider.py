"""LLM provider integration for the AI Advisor - Groq only.

This is the ONLY module that talks to an LLM provider. It is deliberately
isolated from app.advisor (context assembly/grounding) and app.routes.advisor
(HTTP layer) so a different provider or model can be substituted later by
rewriting just this file: the contract is generate_json_reply(system_prompt,
messages) -> raw JSON text, raising only AdvisorConfigError /
AdvisorProviderError.

Security: the API key is read once from GROQ_API_KEY and is never logged,
never included in an exception message, and never returned to a caller.
Only exception *types* and HTTP status codes are logged.
"""
import logging
import os

import groq
from groq import Groq

from app.advisor_errors import AdvisorConfigError, AdvisorProviderError

logger = logging.getLogger("omerpath.advisor.provider")

GROQ_MODEL = "openai/gpt-oss-120b"
REQUEST_TIMEOUT_SECONDS = 30.0
MAX_OUTPUT_TOKENS = 1500

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip() or None


def _get_client() -> Groq:
    if not GROQ_API_KEY:
        raise AdvisorConfigError("GROQ_API_KEY is not configured.")
    return Groq(api_key=GROQ_API_KEY, timeout=REQUEST_TIMEOUT_SECONDS)


def generate_json_reply(system_prompt: str, messages: list[dict[str, str]]) -> str:
    """Sends the assembled system prompt + conversation to Groq and returns
    the raw JSON text of the model's reply.

    Raises AdvisorConfigError (missing/invalid credentials) or
    AdvisorProviderError (timeout, connection failure, non-2xx response, or
    an empty/unusable reply) - never a raw provider exception.
    """
    client = _get_client()

    request_messages = [{"role": "system", "content": system_prompt}, *messages]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_completion_tokens=MAX_OUTPUT_TOKENS,
            messages=request_messages,
            response_format={"type": "json_object"},
        )
    except groq.APITimeoutError as exc:
        logger.error("Advisor provider request timed out | type=%s", type(exc).__name__)
        raise AdvisorProviderError("The Advisor took too long to respond.") from exc
    except groq.AuthenticationError as exc:
        logger.error("Advisor provider authentication failed | type=%s", type(exc).__name__)
        raise AdvisorConfigError("Advisor provider credentials are invalid.") from exc
    except groq.APIConnectionError as exc:
        logger.error("Advisor provider connection error | type=%s", type(exc).__name__)
        raise AdvisorProviderError("The Advisor is temporarily unavailable.") from exc
    except groq.APIStatusError as exc:
        logger.error("Advisor provider error | type=%s | status=%s", type(exc).__name__, exc.status_code)
        raise AdvisorProviderError("The Advisor is temporarily unavailable.") from exc

    choice = response.choices[0] if response.choices else None
    content = choice.message.content if choice and choice.message else None
    if not content:
        logger.error(
            "Advisor provider returned no content | finish_reason=%s",
            getattr(choice, "finish_reason", None),
        )
        raise AdvisorProviderError("The Advisor returned an unusable response.")

    return content
