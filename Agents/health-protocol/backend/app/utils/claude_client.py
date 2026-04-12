"""Claude API client with exponential-backoff retry and JSON parsing."""
from __future__ import annotations

import asyncio
import json

import anthropic

from app.config import settings

# Model identifiers — change here to update everywhere
HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-6"

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def call_claude(
    *,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 1024,
    retries: int = 3,
) -> str:
    """Call Claude and return the raw text response.

    Retries up to `retries` times on rate-limit and 5xx errors with
    exponential backoff starting at 1 second.
    """
    client = get_client()
    delay = 1.0
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except anthropic.RateLimitError as exc:
            last_error = exc
            await asyncio.sleep(delay)
            delay *= 2
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                last_error = exc
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise

    raise RuntimeError(
        f"Claude API call failed after {retries} attempts"
    ) from last_error


async def call_claude_json(
    *,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 1024,
    retries: int = 3,
) -> dict:
    """Call Claude and return a parsed JSON dict.

    If the response is not valid JSON, makes one additional call with a
    JSON-repair prompt before raising ValueError.
    """
    from app.utils.prompts import JSON_FIX_TEMPLATE  # local import avoids circular

    raw = await call_claude(
        model=model,
        system=system,
        user=user,
        max_tokens=max_tokens,
        retries=retries,
    )

    # Strip markdown code fences if Claude wraps the JSON despite instructions
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # drop first line (```json or ```) and last line (```)
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass  # fall through to repair attempt

    # One repair attempt
    fix_prompt = JSON_FIX_TEMPLATE.format(broken_json=cleaned)
    repaired = await call_claude(
        model=model,
        system="Return ONLY valid JSON. No markdown. No preamble.",
        user=fix_prompt,
        max_tokens=max_tokens,
        retries=retries,
    )
    repaired_cleaned = repaired.strip()
    if repaired_cleaned.startswith("```"):
        lines = repaired_cleaned.splitlines()
        repaired_cleaned = "\n".join(
            lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        )

    try:
        return json.loads(repaired_cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Claude returned invalid JSON even after repair attempt: {exc}\n"
            f"Raw response: {raw[:500]}"
        ) from exc
