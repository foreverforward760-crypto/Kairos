# Changes Made

Applied against `claude/pattern-reflection-journal-lvrf6m`. Committed locally as one commit
("Fix Stage 8 naming, add chamber/amplifier fields, configurable persistence + auth/CORS,
negation handling, NSDT reference doc") so you can inspect it with `git log -p` or `git show`
before deciding whether to push.

## 1. Constitutional fix — `sap_kairos_geometry.py`
`STAGE_METADATA_KAIROS[8]["human_name"]` was `"False Heaven / False Hell"`, which is the exact
term your own README calls "constitutionally prohibited across the entire SAPP ecosystem." It
was returned directly via the API's `stage_human_name` field. Changed to `"The Permanence Trap"`
to match the web app, which already had this right.

## 2. Chamber detection + trap_score_amplifier — `sap_kairos_geometry.py`, `sap_kairos_bayesian.py`
The README's example `/analyze` response includes `"chamber"` and `"trap_score_amplifier": 1.45`,
but neither field existed in the actual code. Added:
- `STAGE8_TRAP_SCORE_AMPLIFIER = 1.45` (the constant from your doctrine).
- `classify_stage8_chamber()` — a **first-pass, fully disclosed heuristic** using NSDT axis 0 as
  a valence proxy (>= 5.0 -> "Illusion of Arrival", < 5.0 -> "Illusion of Permanence"). This is
  explicitly documented in its docstring and in `docs/NSDT_REFERENCE.md` as unvalidated — please
  review/replace before relying on it clinically.
- Both fields are now in the `/analyze` response, populated only when `dominant_stage == 8`.

## 3. NSDT reference doc — `docs/NSDT_REFERENCE.md` (new)
The 5-axis input vector was never documented anywhere. This doc separates what's *confirmed* by
code (range, weighting, distance calc) from what's *inferred* (a proposed Connection / Stability /
Tension / Agency / Coherence mapping, based only on the one-letter variable names in
`sap_energy_layer.py`), plus practical scoring guidance for a human populating the vector by hand.
**This is the one change that most needs your sign-off** — if the axis guesses are wrong, fix the
table and the chamber heuristic changes with it.

## 4. Configurable persistence + path traversal fix — `sap_kairos_session.py`, `api_kairos.py`
- `KairosSession` now takes a `data_dir` and sanitizes `system_id` (strips anything but
  `[A-Za-z0-9_-]`) before it's ever used in a file path. Previously, `storage_backend="file"` with
  an untrusted `system_id` like `"../../etc/passwd"` would have let a caller write/read outside
  the intended directory. Tested — confirmed the traversal payload lands safely inside the
  sanitized filename now.
- `api_kairos.py` reads `KAIROS_STORAGE_BACKEND` / `KAIROS_DATA_DIR` env vars and passes them
  through. Default is unchanged (`memory`), so this is backwards compatible.

## 5. Optional API key auth + CORS — `api_kairos.py`
- `KAIROS_API_KEY` env var: if set, `/analyze`, `/history/{id}`, `/reset/{id}` require a matching
  `X-API-Key` header (401 otherwise). `/health` stays open for monitoring. Unset by default — no
  behavior change unless you opt in.
- `KAIROS_ALLOWED_ORIGINS` env var: comma-separated origins; if set, adds `CORSMiddleware`. Unset
  by default — no CORS middleware added at all, same as before.

## 6. Coaching response negation handling — `api_kairos.py`
`generate_coaching_response` matched raw substrings (`"stuck"`, `"scared"`, `"angry"`), so
"I'm not stuck anymore" triggered the stuck-response. Added `_mentioned_without_negation()` — a
small window-based check for common negation cues (`"not "`, `"n't"`, `"no longer"`, etc.) before
a keyword match counts. Still a first-pass heuristic, not real NLP — documented as such in the
code.

## 7. Pydantic v1 -> v2 migration — `api_kairos.py`
`@validator` (deprecated in Pydantic 2.x, still on the version pinned in `requirements.txt`)
replaced with `@field_validator` + `@classmethod`. Same validation logic, no behavior change.

## 8. README updates
- Linked `docs/NSDT_REFERENCE.md` near the API section.
- New "Configuration" section documenting all four env vars with a production-leaning example
  command.
- New "API vs. Reflection Journal — Independent Classifiers" section stating plainly that the
  API and the web app are separate, disagreeing-is-expected methods, so nobody mistakes one for
  a validation check on the other.
- Note under the example response clarifying `chamber`/`trap_score_amplifier` are Stage-8-only.

## What I deliberately did NOT do
- Did not attempt to reconcile or merge the API's Bayesian classifier with the web app's
  digit-root method — that's a product decision, not a bug fix, and I documented the divergence
  instead (item 8).
- Did not add rate limiting or a real auth system (JWT/OAuth) — a single shared API key was the
  smallest change that closes the "wide open on a network" gap without new dependencies or a
  bigger design decision on your end.
- Did not touch the web app (`pattern_reflection_journal.html`) — it didn't have bugs, only the
  Python engine and README did.

## Verification performed
- `python -m py_compile` on every changed `.py` file.
- Direct unit-level calls to `KairosBayesian.forward()` confirming: the Stage 8 human_name fix,
  chamber classification reachable in both directions (found real NSDT vectors landing on each
  chamber via grid search), and the amplifier constant.
- `fastapi.testclient.TestClient` end-to-end tests: `/health`, `/analyze` (happy path, 422 on
  out-of-range `nsdt`), `/history`, `/reset`, API-key auth (401 without key / wrong key, 200 with
  correct key, `/health` still open), and file-backend persistence with a path-traversal attempt
  (confirmed the malicious `system_id` was sanitized and stayed inside the data dir).

## How to apply
Either:
- Unzip `kairos-fixed-repo.zip` — it's the full working tree with `.git` intact, one commit ahead
  of `claude/pattern-reflection-journal-lvrf6m`. Point your own remote at it and push, or
  `git format-patch`/`git log -p` to inspect first.
- Or apply `kairos-changes.patch` to your existing local clone: `git apply kairos-changes.patch`
  (or `git apply --check kairos-changes.patch` first to dry-run).
