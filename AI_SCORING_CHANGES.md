# AI-Assisted NSDT Scoring — What Was Added

New commit on top of the previous fixes: `0e09f4a — Add opt-in AI-assisted NSDT scoring via Claude
(POST /score-nsdt)`.

## New file: `sap_kairos_ai_scoring.py`
- `score_nsdt_from_notes(notes, model=None)` — sends freeform session notes to Claude, gets back a
  proposed 5-axis NSDT vector with per-axis reasoning, a confidence label, and caveats.
- Default model: `claude-sonnet-5` (per your choice), overridable via `KAIROS_AI_SCORING_MODEL`.
- **Claude never sees the stage taxonomy.** The prompt contains only the five axis definitions
  (Connection / Stability / Tension / Agency / Coherence, matching `docs/NSDT_REFERENCE.md`) — not
  `STAGE_CENTROIDS`, stage names, or chamber logic. This was a deliberate call, not an oversight:
  if the model knew what stage a given vector would produce, it could reverse-engineer a
  "convenient" answer instead of independently reading the notes. Verified with a unit test that
  asserts none of the stage-taxonomy strings appear in the actual prompt sent.
- Defensive JSON parsing: handles code-fenced responses, clamps out-of-range values into 0–10,
  and raises a clear `AIScoreError` (surfaced as HTTP 502) rather than silently returning a
  guessed or malformed vector.

## New endpoint: `POST /score-nsdt` — `api_kairos.py`
- Returns `503` unless the operator has set **both** `KAIROS_ENABLE_AI_SCORING=true` and
  `ANTHROPIC_API_KEY` — matches the "server switch only" design you picked, no per-request flag.
- Reuses the existing `X-API-Key` auth dependency, so it's covered by whatever auth you already
  have configured on the rest of the API.
- Response always includes a `disclosure` field stating plainly that the notes were sent to
  Anthropic's API and that this is a proposed starting point, not a finished score.
- **Does not call `/analyze` itself.** Chaining the proposed vector into `/analyze` is a separate,
  deliberate second request — confirmed in testing (score → inspect → manually POST to /analyze).

## `requirements.txt`
Added `anthropic==0.116.0` (latest on PyPI as of this session).

## README.md / docs/NSDT_REFERENCE.md
Documented the endpoint, the two new env vars, and the "why Claude doesn't see the taxonomy"
rationale in both places so it doesn't get lost.

## Verification performed
- `python -m py_compile` on the new/changed files.
- Confirmed `/score-nsdt` returns `503` with no env vars set (default-off behavior).
- Unit-tested the JSON extraction/validation logic directly: clean JSON, code-fenced JSON,
  out-of-range clamping, and rejection of a malformed (wrong-length) response.
- Full endpoint test with a **mocked** Claude response (`unittest.mock.patch` on
  `anthropic.Anthropic`): confirmed `200` with `nsdt`/`reasoning`/`confidence`/`caveats`/
  `disclosure`/`system_id` in the response, confirmed a malformed model response correctly
  produces `502` instead of silently failing, and confirmed the proposed vector can be manually
  chained into `/analyze` afterward.
- Grepped the actual prompt text sent to the (mocked) client and asserted none of
  `PLENARA`, `VESSEL OF GROUNDING`, `STAGE_CENTROIDS`, `Illusion of Arrival`, `chamber` appear in
  it — confirming the taxonomy-blindness design is actually enforced in code, not just documented.

## What I could NOT test
I don't have an Anthropic API key in this environment, so **the actual live call to Claude has not
been tested end-to-end** — only the request-building, response-parsing, and error-handling logic
around it, using a mocked client. Before relying on this in production: set
`KAIROS_ENABLE_AI_SCORING=true` and a real `ANTHROPIC_API_KEY`, then run a real `/score-nsdt` call
against a few sample notes and sanity-check the reasoning quality yourself — prompt wording is the
one thing that's genuinely hard to validate without a live model in the loop.

## How to apply
`git apply kairos-ai-scoring.patch` on top of your already-pushed `182cfe4` commit, or copy
`sap_kairos_ai_scoring.py` in fresh and apply the diffs to `api_kairos.py`, `README.md`,
`docs/NSDT_REFERENCE.md`, and `requirements.txt` shown in the patch.
