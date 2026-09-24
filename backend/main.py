import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.config import get_settings
from backend.gemini_client import GeminiAPIError, ask_astrologer
from backend.models import AskRequest, AskResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Astrology AI Assistant")


@app.on_event("startup")
def validate_config() -> None:
    # Fail fast if GEMINI_API_KEY (or other required settings) is missing.
    get_settings()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    settings = get_settings()

    if len(request.query) > settings.max_query_length:
        raise HTTPException(
            status_code=422,
            detail=f"query must be at most {settings.max_query_length} characters",
        )

    try:
        result = await ask_astrologer(request.query, settings)
    except GeminiAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        return AskResponse(**result)
    except ValidationError as exc:
        logger.error("Response failed output validation: %s", exc)
        raise HTTPException(
            status_code=502, detail="The astrology service returned an invalid response."
        ) from exc


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error while processing request")
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})
