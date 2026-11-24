
import logging
import re
from typing import Any

import litellm
from litellm import Cache, completion

from app.config import API_KEY_POOL, DEFAULT_SYSTEM_PROMPT, LLM_MODEL

logger = logging.getLogger("uvicorn.error")

# LiteLLM built-in in-memory cache
litellm.cache = Cache(type="local")


class AllProvidersUnavailable(Exception):
    """Raised when every configured provider key fails."""


def parse_failure_header(
    header_value: str | None,
    enabled: bool,
) -> dict[str, int]:
    if not header_value or not enabled:
        return {}

    failures = {}

    for item in header_value.split(","):
        item = item.strip()

        if not item:
            continue

        match = re.fullmatch(r"(key_\d+|\*)=(429|500|502|503)", item)

        if not match:
            raise ValueError("Invalid X-Simulate-Failure header")

        key_id, status_code = match.groups()
        failures[key_id] = int(status_code)

    return failures


def _is_cache_hit(response: Any) -> bool:
    hidden_params = getattr(response, "_hidden_params", {}) or {}

    return bool(
        hidden_params.get("cache_hit")
        or hidden_params.get("cached")
    )


def _get_token_usage(response: Any) -> tuple[int, int]:
    usage = getattr(response, "usage", None)

    if usage is None:
        return 0, 0

    input_tokens = getattr(usage, "prompt_tokens", 0) or 0
    output_tokens = getattr(usage, "completion_tokens", 0) or 0

    return int(input_tokens), int(output_tokens)


def generate_response(
    user_message: str,
    history: list[dict[str, str]],
    system_prompt: str | None = None,
    simulated_failures: dict[str, int] | None = None,
) -> dict[str, Any]:

    if not API_KEY_POOL:
        raise AllProvidersUnavailable()

    simulated_failures = simulated_failures or {}
    active_system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    messages = [
        {"role": "system", "content": active_system_prompt},
        *history,
        {"role": "user", "content": user_message},
    ]

    fallback_attempts = 0

    for key_config in API_KEY_POOL:
        key_id = key_config["key_id"]
        api_key = key_config["api_key"]

        simulated_status = simulated_failures.get(
            key_id,
            simulated_failures.get("*"),
        )

        if simulated_status is not None:
            logger.warning(
                "Simulated HTTP %s failure for %s",
                simulated_status,
                key_id,
            )
            fallback_attempts += 1
            continue

        try:
            response = completion(
                model=LLM_MODEL,
                messages=messages,
                api_key=api_key,
                caching=not bool(simulated_failures),
            )

            reply = response.choices[0].message.content

            if not reply:
                raise ValueError("Provider returned an empty response")

            input_tokens, output_tokens = _get_token_usage(response)
            cache_hit = _is_cache_hit(response)

            return {
                "reply": str(reply),
                "metadata": {
                    "resolution_source": (
                        "LLM_CACHE" if cache_hit else "LIVE_INFERENCE"
                    ),
                    "model": LLM_MODEL,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "key_id": None if cache_hit else key_id,
                    "fallback_attempts": (
                        0 if cache_hit else fallback_attempts
                    ),
                },
            }

        except Exception as exc:
            # Log the actual provider error without exposing API keys.
            error_message = str(exc)
            error_message = re.sub(
                r"AIza[0-9A-Za-z_-]{20,}",
                "[REDACTED_API_KEY]",
                error_message,
            )

            logger.error(
                "Provider attempt failed for %s. Error: %s: %s",
                key_id,
                type(exc).__name__,
                error_message[:500],
            )

            fallback_attempts += 1

    raise AllProvidersUnavailable()
