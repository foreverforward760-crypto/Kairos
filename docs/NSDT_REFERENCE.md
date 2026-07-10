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

## Stage classifier reconciliation (resolved) + one remaining legacy piece

An earlier version of this document flagged a real, load-bearing conflict:
`STAGE_CENTROIDS`/`AXIS_WEIGHTS` (`sap_kairos_geometry.py`) — the Bayesian
classifier that decides `dominant_stage` in `/analyze` — were built, before
the canonical framework materials were available, against a *different*,
guessed axis order (`c, s, t, a, coh` — Connection, Stability, Tension,
Agency, Coherence), which conflicted with the confirmed N/S/D/T/C order on
3 of 5 positions.

**`STAGE_CENTROIDS` has since been rebuilt from scratch against the
confirmed axes** (see the derivation comment directly above
`STAGE_CENTROIDS` in `sap_kairos_geometry.py`). No canonical centroid table
exists anywhere in the SAPP source material, so there was never a "correct"
table to restore — instead, Stability and Coherence for every stage are
now *solved* from the confirmed `compute_inversion()` formulas so that each
stage's known parity is produced by construction (verified by round-tripping
every centroid back through `compute_inversion()`), Tension and
Adaptability are seeded from each stage's existing `polyvagal` field rather
than invented fresh, and Complexity — which has no formula pull anywhere in
`compute_inversion()` — is an explicit, disclosed standalone curve.
Axis *direction* is now formula-guaranteed correct for every stage; the
specific depth of each value is still an engineering judgment call, not
something validated against real client data.

**`SAPEnergy.trap_energy()` (`sap_energy_layer.py`) was deliberately left
as legacy, not reconciled.** Unlike the centroids, its specific
coefficients (`2.0*coh - 1.5*a + 1.2*s`, etc.) have no formula in the
Tumbling Inversion material to re-derive them from — re-guessing them would
just trade one unverified guess for another. It's marked legacy in its own
docstring. For Stage 6/7/8, prefer the real `stage_paradox` field over
`trap_energy()`'s output (`chamber`/`trap_score_amplifier` in the API
response); those two fields are kept only for backward compatibility, not
because they're the more trustworthy read of Stage 8.

**A second, more consequential bug was found and fixed while verifying the
rebuilt centroids.** `KairosBayesian.posterior()` (`sap_kairos_bayesian.py`)
used to call `SAPEnergy.modulate_logits()`, which subtracts
`beta * trap_energy(stage, x)` from every stage's logit *before* the argmax
that picks `dominant_stage` — meaning legacy-axis trap energy was silently
steering stage classification itself, not just the informational fields.
Feeding each rebuilt centroid straight back into `/analyze` (it should
trivially classify as its own stage) caught this directly: Stage 8's own
centroid was being classified as Stage 4, because the legacy-axis trap
energy computed for Stage 8 on that vector outweighed its otherwise-zero
distance in the nearest-centroid calculation. `posterior()` no longer calls
`modulate_logits()` — `dominant_stage` is now pure nearest-centroid distance
on the confirmed axes, full stop. `trap_energy()` is still computed *after*
a stage is chosen and still drives the informational `trap_energy`,
`chamber`, and `trap_score_amplifier` fields; it just no longer gets a vote
in which stage is chosen. All 10 rebuilt centroids now self-classify
correctly when round-tripped through `/analyze`.

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
