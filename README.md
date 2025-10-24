# Adaptive English Level Test

This repository implements a full-stack prototype of a computerized adaptive English placement test that follows the CAT + IRT specification described in `docs/TZ_v3.md`.

## Features
- FastAPI backend that exposes endpoints for starting a session, requesting items, submitting answers, tracking listening plays, and finishing the test.
- Python CAT engine that supports 2PL/3PL/GPCM scoring, MAP ability updates, Fisher information based item selection, and per-session item histories.
- Rich sample item bank with 150 tasks per domain (Vocabulary, Grammar, Listening, English in Use) across a range of difficulties.
- Single-page web interface served from `/` that lets you manually explore the adaptive flow end to end.

## Running locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the FastAPI app:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Open http://127.0.0.1:8000/ in a browser to access the UI. The SPA consumes the documented REST API from the backend.

## Testing
Execute the automated tests with:
```bash
pytest
```

The suite covers the adaptive engine calculations, domain transitions, and the REST workflow including the two-play listening guardrail.
