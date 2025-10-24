# Adaptive English Level Test

This repository implements a full-stack prototype of a computerized adaptive English placement test that follows the CAT + IRT specification described in `docs/TZ_v3.md`.

## Features
- Lightweight standard-library HTTP server that exposes endpoints for starting a session, requesting items, submitting answers, tracking listening plays, and finishing the test.
- Python CAT engine that supports 2PL/3PL/GPCM scoring, MAP ability updates, Fisher information based item selection, and per-session item histories.
- Rich sample item bank with 150 tasks per domain (Grammar, Vocabulary, English in Use, Listening) across a range of difficulties and listening question types (multiple-choice plus true/false).
- Sequential section flow that pauses between Grammar → Vocabulary → English in Use → Listening, with a running timer and required candidate name capture.
- Single-page web interface served from `/` that lets you manually explore the adaptive flow end to end and stores every test run in a local SQLite database.

## Running locally
1. (Optional) Create a virtual environment.
2. Run the bundled development server:
   ```bash
   python -m app.server
   ```
3. Open http://127.0.0.1:8000/ in a browser to access the UI. Enter a first and last name, choose a starting level, and follow the pauses between sections to progress through the full test.

## Testing
Execute the automated tests with:
```bash
pytest
```

The suite covers the adaptive engine calculations, domain transitions with pause/resume handling, persistence to SQLite, and the REST workflow including the two-play listening guardrail.
