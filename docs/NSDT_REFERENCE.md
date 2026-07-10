# NSDT Vector Reference

`nsdt` is the primary input to `POST /analyze` and (via AI estimation from
freeform text) to `POST /reading` — a 5-element array of numbers, each in
`[0.0, 10.0]`:

```json
"nsdt": [6.2, 4.5, 7.8, 3.2, 5.1]
```

## Confirmed axis definitions

As of this update, the axis meanings are **confirmed**, not inferred —
sourced directly from the user's own authored and tested Tumbling Inversion
module (`tumbling_inversion.py`'s docstring, `TUMBLING_INVERSION_v8.2.md`,
and validated by running the user's own 25-test suite,
`test_tumbling_inversion.py`, unmodified against the ported implementation):

| Index | Letter | Axis | Meaning |
|---|---|---|---|
| 0 | N | Complexity | How many moving parts / competing threads are present |
| 1 | S | Stability | How settled, secure, or held the situation feels |
| 2 | D | Adaptability | Active capacity to adjust, respond, integrate what's happening |
| 3 | T | Tension | Felt pressure, unresolved conflict, strain (the framework's "Polarity Load") |
| 4 | C | Coherence | Internal narrative consistency / clarity of the account |

This is the vector `sap_kairos_tumbling_inversion.py` and
`sap_kairos_stage_paradox.py` operate on — the actual Tumbling Inversion
Principle math (physical/consciousness stability by stage parity, the
Stage 5 Middle Path Gateway, Stage 6 Conductor's Paradox, Stage 7
Individuation Crucible, Stage 8 Crystallization Paradox + Gratitude
Mechanism) runs directly against these five numbers, not a description of
them.

**Scale note:** `/analyze` and `/reading` keep the public `0.0–10.0`
contract described above (matching `KairosInput.validate_nsdt` and the
AI-estimation prompts). The Tumbling Inversion formulas themselves are
written against a `0–100` scale (every threshold in
`TUMBLING_INVERSION_v8.2.md` and the user's test suite — `50`, `70`, `55`,
`100-T`, etc. — assumes `0–100`). `api_kairos.py`'s
`compute_tumbling_inversion_state()` bridges this with a single, centralized
`× 10` rescale immediately before calling any Tumbling Inversion function —
that is the one seam where the public 0–10 contract meets the framework's
native 0–100 scale. `physical_stability`, `consciousness_stability`,
`divergence`, and `witness_score`/`conductor_score`/`distillation_score` in
API responses are all on the native `0–100` scale, by design — they are not
supposed to look like the input vector.

## ⚠ Known inconsistency: the *stage classifier* still uses the old, superseded axes

Before the user's canonical framework materials were available, this
project's `STAGE_CENTROIDS`/`AXIS_WEIGHTS` (`sap_kairos_geometry.py`) and
`SAPEnergy.trap_energy()` (`sap_energy_layer.py`) — which is to say, **the
Bayesian classifier that decides `dominant_stage` in `/analyze`, and the
chamber/trap-energy detection** — were built against a *different*, guessed
axis order: `c, s, t, a, coh` (Connection, Stability, Tension, Agency,
Coherence), unpacked directly in `trap_energy()`.

That guess is **not** the same as the confirmed N/S/D/T/C order above.
Indices 1 (Stability) and 4 (Coherence) happen to agree; indices 0, 2, and 3
do not (index 0 is read as Connection by the classifier and Complexity by
Tumbling Inversion; index 2 as Tension vs. Adaptability; index 3 as Agency
vs. Tension). Both systems currently read the *same* `inp.nsdt` array in
`/analyze` with genuinely different interpretations of three of its five
positions.

This is a real, load-bearing conflict, not a documentation nitpick — it
means `dominant_stage` (which of the 10 stages the classifier says you're
in) and `trap_energy`/chamber detection are still running on the older,
unconfirmed guess, while everything under `tumbling_inversion` in the API
response (parity, physical/consciousness stability, divergence, geometric
form, arc direction, Middle Path, stage paradox, disruption loops) runs on
the confirmed, framework-native axes. Reconciling `STAGE_CENTROIDS` and
`trap_energy()` to the confirmed axis order is real follow-up work — it
wasn't done as part of this update because no canonical centroid values
exist in any of the user's source materials to rebuild it against (the
`STAGE_CENTROIDS` table has always been this project's own engineering
approximation, not something from the SAPP corpus). Until that's done,
treat `dominant_stage` as a reasonable-but-unverified stage pick, and
treat everything in the `tumbling_inversion` block as the verified,
framework-faithful part of the response.

## Practical scoring guidance

There's no validated intake instrument in this repo for turning a
conversation into five numbers by hand. A defensible interim approach for a
practitioner populating `nsdt` directly:

1. Score each axis 0–10 based on what's actually in the notes/text, not a
   computed formula.
2. Treat 5.0 as "unclear/mixed signal, don't force a number" rather than
   inventing precision.
3. Re-score per session rather than reusing a stale vector — the session
   tracker (`sap_kairos_session.py`) turns snapshots into a trend (arc
   direction, sticky Middle Path); a single reading isn't meant to stand
   alone.
4. Don't backfill "smoother" numbers to make the posterior look more
   confident. The `entropy` field is meaningful precisely because
   low-confidence, spread-out posteriors are honest information.

## AI-assisted scoring (optional, off by default)

Two separate AI scorers exist, and they are **not interchangeable**:

- `POST /score-nsdt` (`sap_kairos_ai_scoring.py`) — practitioner-facing,
  scores freeform session notes onto the **old** `c, s, t, a, coh` axes
  (same ones `trap_energy()` uses), for backward compatibility with the
  existing Bayesian classifier. The model is never shown `STAGE_CENTROIDS`
  or stage names.
- `POST /reading`'s internal estimation (`sap_kairos_nsdt_estimator.py`) —
  used automatically for the consumer AI reading, scores freeform text onto
  the **confirmed** N/S/D/T/C axes above, feeding the real Tumbling
  Inversion engine. The model is never shown Tumbling Inversion thresholds,
  stage names, or geometric forms — same anti-circularity rule.

Both return a confidence label; neither is meant to be trusted blindly.
