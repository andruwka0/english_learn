# Adaptive English Level Test

This repository implements a full-stack prototype of a computerized adaptive English placement test that follows the CAT + IRT specification described in `docs/TZ_v3.md`.

## Features
- Lightweight standard-library HTTP server that exposes endpoints for starting a session, requesting items, submitting answers, tracking listening plays, and finishing the test.
- Python CAT engine that supports 2PL/3PL/GPCM scoring, MAP ability updates, Fisher information based item selection, and per-session item histories.
- Rich sample item bank with 150 tasks per domain (Vocabulary, Grammar, Listening, English in Use) across a range of difficulties.
- Single-page web interface served from `/` that lets you manually explore the adaptive flow end to end.

## Running locally
1. (Optional) Create a virtual environment.
2. Run the bundled development server:
   ```bash
   python -m app.server
   ```
3. Open http://127.0.0.1:8000/ in a browser to access the UI. The single-page app consumes the documented REST API from the bundled backend.

## Testing
Execute the automated tests with:
```bash
pytest
```

The suite covers the adaptive engine calculations, domain transitions, and the REST workflow including the two-play listening guardrail.
