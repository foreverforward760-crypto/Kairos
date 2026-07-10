# NSDT Vector Reference

`nsdt` is the primary input to `POST /analyze` — a 5-element array of numbers,
each in `[0.0, 10.0]`:

```json
"nsdt": [6.2, 4.5, 7.8, 3.2, 5.1]
```

**This document exists because the rest of the repo never spells out what the
five numbers mean.** What follows is split explicitly into what's *confirmed*
by the code, and what's a *best-effort inference* that still needs sign-off
from whoever defined the original SAPP axes — in keeping with this project's
own stated principle (see `webapp/README.md`) of not presenting inferred
precision as settled fact.

## Confirmed (from code)

- It's a 5-dimensional vector, values clamped to `0.0–10.0` (`KairosInput.validate_nsdt`
  in `api_kairos.py` rejects anything outside that range, or NaN/Inf).
- Each of the 10 stage centroids in `sap_kairos_geometry.py` (`STAGE_CENTROIDS`)
  is a point in this same 5D space — the engine classifies a client by
  weighted Euclidean distance from `nsdt` to each centroid (see
  `KairosBayesian._weighted_distance`).
- Axes are not weighted equally: `AXIS_WEIGHTS = [1.0, 1.5, 1.5, 1.0, 0.8]`
  (`sap_kairos_geometry.py`) — axes 1 and 2 (0-indexed) count 1.5x as much as
  axis 4, and 1.5x more than axes 0 and 3, in the distance calculation.
- `sap_energy_layer.py`'s `SAPEnergy.trap_energy()` unpacks the vector as
  `c, s, t, a, coh = x` — these five one/two-letter names are the *only*
  textual clue to axis identity anywhere in this repo.

## Inferred (best guess, unconfirmed — please correct in code + here)

Based on the variable names above and how each axis is used in
`trap_energy()` and `KairosGeometry`, axis-by-axis:

| Index | Code letter | Best-guess meaning | Basis for the guess |
|---|---|---|---|
| 0 | `c` | Connection | Combined with `coh` in the Stage 5 trap formula as a joint "alignment" term; used as the Stage 8 chamber valence proxy in this update (see below) — reasonable but not confirmed. |
| 1 | `s` | Stability / Safety | Positively drives Stage 8 trap energy (`+1.2*s`); reads as "how settled/secure the state feels," which fits Stage 8's certainty trap. |
| 2 | `t` | Tension / Threat | Drives Stage 7 trap energy (`+1.5*t`); highest-weighted axis in classification (1.5x) alongside `s`. |
| 3 | `a` | Agency | Explicitly named in Stage 3 (`a - 7.0`) and Stage 5 (`4.0 - a`) trap formulas; low agency increases Stage 5 trap, consistent with "agency" as a choice-point variable. |
| 4 | `coh` | Coherence | Spelled out in variable name; drives Stage 8 trap energy most strongly (`+2.0*coh`), consistent with "internal narrative coherence/certainty." |

**None of these five labels are declared as constants anywhere in the code.**
If they're correct, promote them to a real `AXIS_NAMES` list in
`sap_kairos_geometry.py` so they stop being tribal knowledge. If they're
wrong, this table is the thing to fix first — everything else in this repo
(chamber classification, coaching copy, README examples) assumes some
version of this mapping is right.

## Practical scoring guidance (until something more rigorous exists)

There's no validated intake instrument in this repo for turning a
conversation into five numbers. Until one exists, a defensible interim
approach for a therapist/coach populating `nsdt` by hand:

1. Score each axis 0–10 based on the client's own language and affect in the
   session, not a computed formula.
2. Treat 5.0 as "unclear/mixed signal, don't force a number" — the engine's
   Stage 5 centroid is close to the midpoint on several axes, so genuine
   ambivalence should land near the choice-point stage rather than being
   forced toward a pole.
3. Re-score per session rather than reusing a stale vector — the session
   tracker (`sap_kairos_session.py`) is what turns single snapshots into a
   trend; a single `nsdt` reading is not meant to stand alone.
4. Don't backfill "smoother" numbers to make posteriors more confident. The
   `entropy` field in the response is meaningful precisely because low-
   confidence, spread-out posteriors are honest information, not noise to
   suppress.

## AI-assisted scoring (optional, off by default)

`POST /score-nsdt` (see main README) uses Claude to propose a vector from freeform notes, using
exactly the axis table above (see `AXIS_DEFINITIONS` in `sap_kairos_ai_scoring.py` — keep the two
in sync if you change either one). The model is deliberately not shown `STAGE_CENTROIDS` or any
stage/chamber names, so it can't work backward from "what stage would this produce" — it only ever
sees the same unconfirmed axis guesses documented above, and is told explicitly that they're
unconfirmed. Output includes a confidence label and caveats, and is meant to be reviewed and
adjusted by a practitioner, not submitted directly to `/analyze`.

## Where this is used elsewhere in this repo

The Stage 8 chamber classifier added in this update
(`classify_stage8_chamber` in `sap_kairos_geometry.py`) uses axis 0 (`c`) as
a valence proxy: `>= 5.0` reads as Chamber A ("Illusion of Arrival"), `< 5.0`
as Chamber B ("Illusion of Permanence"). That choice is downstream of the
same unconfirmed guess in this document — see the docstring on that function
for the full caveat.
