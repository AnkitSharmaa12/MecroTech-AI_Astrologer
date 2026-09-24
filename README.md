# AI Astrologer

A simple AI application that answers astrology-related questions, powered by the
Gemini API (`gemini-2.0-flash`, free tier), served through a FastAPI backend with a
Streamlit UI.

## Stack

- **Backend:** FastAPI (`/ask` endpoint, Pydantic request/response validation, error handling)
- **LLM:** Google Gemini API, `gemini-2.0-flash`
- **Frontend:** Streamlit

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Gemini API key (get one free at
   [aistudio.google.com/apikey](https://aistudio.google.com/apikey)):

   ```bash
   copy .env.example .env
   ```

   Then edit `.env`:

   ```
   GEMINI_API_KEY=your-actual-key-here
   ```

## Run

**Start the backend** (from the project root):

```bash
uvicorn backend.main:app --reload --port 8000
```

**Start the frontend** (in a separate terminal, from the project root):

```bash
streamlit run frontend/app.py
```

The Streamlit app will open in your browser and talk to the backend at `http://localhost:8000`.

## How it works

- The backend sends every user query to Gemini with a system instruction that sets the
  assistant's role as a professional astrologer, and instructs it to only answer
  astrology-related questions.
- The model is asked to respond as JSON (`{"in_scope": bool, "answer": str}`) via
  Gemini's structured output (`response_schema`), which the backend then validates
  against a Pydantic model before returning it to the UI.
- Out-of-scope questions get a polite decline instead of an answer.
- API/network failures, timeouts, invalid keys, and malformed model responses are all
  caught and returned as clean error messages (never raw stack traces).

## Endpoints

- `POST /ask` - body: `{"query": "<question>"}`, returns `{"answer": str, "in_scope": bool}`
- `GET /health` - health check
"# MecroTech-AI_Astrologer" 
