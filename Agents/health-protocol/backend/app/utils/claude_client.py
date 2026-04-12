# Claude API client with exponential-backoff retry — placeholder
import asyncio
import anthropic

from app.config import settings

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
