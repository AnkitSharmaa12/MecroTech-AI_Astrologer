import json
import logging

import httpx

from backend.config import Settings

logger = logging.getLogger(__name__)

GEMINI_GENERATE_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

SYSTEM_PROMPT = (
    "You are a professional astrologer. You only answer questions related to "
    "astrology - zodiac signs, horoscopes, birth charts, planetary influences, "
    "compatibility, transits, and similar topics.\n\n"
    "If the user's question is not related to astrology, do not answer it. "
    "Instead, politely explain that you can only help with astrology-related "
    "topics.\n\n"
    "Always respond with a single JSON object and nothing else, using exactly "
    "this shape:\n"
    '{"in_scope": true or false, "answer": "your reply as plain text"}\n\n'
    "Set \"in_scope\" to true only if the question was astrology-related and "
    "you answered it. Set it to false if you declined because the question "
    "was out of scope."
)

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "in_scope": {"type": "BOOLEAN"},
        "answer": {"type": "STRING"},
    },
    "required": ["in_scope", "answer"],
}


class GeminiAPIError(Exception):
    """Raised when the Gemini API call fails or returns an unusable response."""


async def ask_astrologer(query: str, settings: Settings) -> dict:
    url = GEMINI_GENERATE_URL_TEMPLATE.format(model=settings.gemini_model)
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": query}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": RESPONSE_SCHEMA,
            "temperature": 0.7,
        },
    }
    headers = {
        "x-goog-api-key": settings.gemini_api_key,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException as exc:
        raise GeminiAPIError("The astrology service timed out. Please try again.") from exc
    except httpx.RequestError as exc:
        raise GeminiAPIError("Could not reach the astrology service.") from exc

    if response.status_code in (401, 403):
        raise GeminiAPIError("Invalid Gemini API key.")
    if response.status_code == 429:
        raise GeminiAPIError("Rate limit exceeded. Please try again shortly.")
    if response.status_code >= 400:
        logger.error("Gemini API error %s: %s", response.status_code, response.text)
        raise GeminiAPIError("The astrology service returned an error.")

    try:
        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, ValueError) as exc:
        raise GeminiAPIError("Unexpected response from the astrology service.") from exc

    try:
        parsed = json.loads(content)
        answer = str(parsed["answer"])
        in_scope = bool(parsed["in_scope"])
    except (json.JSONDecodeError, KeyError, TypeError):
        logger.warning("Falling back to raw content, could not parse JSON: %s", content)
        answer = content
        in_scope = True

    return {"answer": answer, "in_scope": in_scope}
