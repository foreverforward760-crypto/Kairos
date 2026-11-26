# LUMINARK Kairos — Reflection and Journaling Prototype

Kairos is an experimental reflection and journaling application built around the owner's 0-9-0 / Stanfield's Axiom of Perpetuity framework. The project owner states that the underlying concepts originated with him; AI systems generated the code and proposed supporting implementation mechanisms.

## What it contains

- A self-contained browser journal with Pattern Scan, Cycle Journal, Habit Log, and stage-reference views.
- A FastAPI backend for supplied NSDT vectors, session history, stage classification, and optional AI-generated reflection text.
- A weighted nearest-centroid classifier that converts a five-axis NSDT vector into a stage distribution using hand-engineered centroids and a softmax.
- Deterministic project-defined formulas for the Tumbling Inversion outputs, stage-parity labels, divergence, and arc-direction heuristics.
- Optional Anthropic integration for proposing NSDT scores from text and generating narrative reflections.

## Important distinction: deterministic code is not empirical validation

The engine does execute formulas and return repeatable outputs for the same inputs. That does not establish that the formulas measure physical stability, consciousness, trauma, nervous-system states, or therapeutic progress.

The centroid table is manually engineered. It was not trained or validated against an independent dataset of people or clinical outcomes. NSDT values entered by a person are subjective ratings; values estimated by an LLM are AI-generated estimates, not measurements.

The class named KairosBayesian is a legacy name: the current classifier uses weighted distance to stage centroids followed by softmax. It does not implement a fitted Bayesian prior/likelihood model.

The project's 'physical stability', 'consciousness stability', 'divergence', 'polyvagal' and 'trap' labels are internal framework indices and interpretations. They are not physiological or psychological measurements.

**Kairos is a reflection/journaling prototype, not therapy, diagnosis, treatment, crisis assessment, or a substitute for professional care.**

## Browser journal

Open webapp/pattern_reflection_journal.html directly in a browser. The base journal uses local browser storage and does not require a server. The digit-root calculation is intentionally presented as a reflective pattern prompt, not as a measurement of the submitted text.

The AI-enabled webapp/kairos_app.html can optionally call a running backend. When AI deep-reading is enabled, submitted text is sent to the configured backend and Anthropic's Claude API. AI-generated story or quote parallels may be inaccurate or misattributed; verify source details independently.

## Backend setup

Install the dependencies:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Local-only development without an API key must be explicitly enabled and bound to loopback:

```bash
KAIROS_ALLOW_INSECURE_LOCAL=true uvicorn api_kairos:app --host 127.0.0.1 --port 8002
```

For any non-local deployment, set a strong KAIROS_API_KEY. Protected endpoints reject requests without a valid key. KAIROS_ALLOW_INSECURE_LOCAL only permits loopback requests and must not be used on a network-facing service.

Optional settings:
- KAIROS_STORAGE_BACKEND=memory (default) or file.
- KAIROS_DATA_DIR for file-backed session JSON.
- KAIROS_ALLOWED_ORIGINS for a comma-separated exact CORS origin allowlist.
- KAIROS_ENABLE_AI_SCORING=true plus ANTHROPIC_API_KEY to enable AI-proposed NSDT scoring.
- KAIROS_ENABLE_AI_READINGS=true plus ANTHROPIC_API_KEY to enable AI-generated readings.

## Privacy and security limitations

- File-backed sessions are plain JSON files, not encrypted records.
- Sessions are keyed by caller-supplied system_id; a shared API key does not provide per-user authorization or account isolation.
- Memory-backed sessions are process-local and are not shared across multiple workers.
- AI scoring and AI readings send the submitted text to Anthropic when enabled.
- Do not send highly sensitive journal entries to a hosted backend without a separate privacy and security review.

## Tests

Run the repository tests with:

```bash
pip install -r requirements.txt pytest
pytest tests -q
```

These tests check selected code paths and formula behavior. They do not validate clinical effectiveness, psychological accuracy, or real-world predictive performance.

## Attribution and commercial review

The project owner's statement about conceptual origin is recorded here, not legally adjudicated. Code authorship, third-party dependencies, model-provider terms, and transferable commercial rights require separate provenance and license review.