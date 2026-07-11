# Stage Disruption Loops (the Seven "Sins" as Structural Loops)

`sap_kairos_disruption_loops.py` ports the "Seven Deadly Sins as Frequency
Disruptions" section of the canonical SAPP corpus
(`SAPP_AppliedArchitecture_v5_FINAL.html`, Section VII) — reframed there, in
the source material itself, as **self-perpetuating structural loops at
specific stages**, not moral failings. Each loop describes a mechanism by
which a stage's natural forward motion gets caught in a closed cycle instead
of continuing to the next stage, plus the "ascending antidote" that breaks
it.

This is exposed in the API as `disruption_loop` inside the
`tumbling_inversion` block of both `/analyze` and `/reading` responses.
Currently it fires only for the one pattern this codebase already had a
deterministic detector for before this update: `KairosSession.detect_cynical_loop()`
(an 8→7→8 or repeated 7/8 alternation over the recent history), which maps to
the **Wrath** loop below — see `loop_for_cynical_pattern()` in
`sap_kairos_disruption_loops.py`. The other six loops are documented here for
reference and future wiring (each would need its own detector against the
NSDT history; none is invented or guessed at here, all seven are from the
source document verbatim).

| Sin | Loop location | Mechanism | Ascending antidote |
|---|---|---|---|
| **Pride** | Stage 8 — First Solidification | The self constructs itself as fixed and uniquely significant. Any challenge reads as threat, producing more rigidity, making the self harder to examine — each recognized limitation gets reframed as more proof of uniqueness. | **Humility** — not self-diminishment, accurate self-assessment held without defensiveness. |
| **Greed** | Stage 6 Material Density + Stage 8 | The self identifies with what it has. Each acquisition delivers brief Stage 6 satisfaction that reverts to baseline lack, read as evidence more is needed. "Enough" stays structurally unavailable while the self is identified with having rather than being. | **Generosity** — loosening identification with accumulation; each real act of giving re-establishes that the self is prior to what it holds. |
| **Lust** | Stage 2 Polarity Short-Circuit + Stage 5 Filter Collapse | Simulated encounter delivers the charge of genuine polarity without its substance, so the Stage 5 filter that selects for real resonance atrophies from disuse, degrading capacity for the real encounter further. | **Genuine encounter** — real stakes, real vulnerability, real consequence; holding the threshold instead of collapsing it immediately. |
| **Envy** | Stage 4 Comparison Overload — Ground Erosion | The stable ground of Stage 4 gets replaced with constantly shifting comparison to others. Since there's always someone with more, the lack becomes structurally permanent. | **Gratitude** — returning the self's reference point to its own position instead of its position relative to others. |
| **Gluttony** | Stage 6 Sensory Overload — Prism Numbing | Overconsumption dulls the discrimination Stage 7 distillation needs. Each cycle of excess requires more stimulation for the same charge, dulling sensitivity further until there's nothing distinct left to distill from. | **Temperance** — not abstinence, calibration: choosing experience at the intensity where discrimination is still possible. |
| **Wrath** | Stage 6 High-Amplitude Polarity — Fake Stage 7 | Anger at maximum amplitude feels like clarity because of its intensity, not because it is clarity. Each cycle produces a felt sense of moral insight that justifies the next cycle as necessary truth-telling rather than disruption. | **Patience** — holding the threshold before acting, to tell a genuine moral response apart from a frequency disruption wearing its clothes. |
| **Sloth** | Stage 7 Avoidance + Stage 8 Inertia | The refusal of the inward work Stage 7 distillation requires, in favor of comfortable Stage 6 stimulation. Each avoidance reinforces the belief that the current state is permanent and no other state is available. | **Diligence** — applied inward: sitting with genuine complexity long enough for something to distill. |

## Why only Wrath is wired up

The other six loops are real content but would each need their own
detector — a pattern read off NSDT history or stage-transition history that
plausibly indicates that specific loop, the same way `detect_cynical_loop()`
already does for the 7/8 alternation that maps to Wrath. Wiring one loop
without a real detection basis for the rest, rather than guessing at
detectors for content that wasn't asked for, keeps this consistent with the
rest of this update: the framework runs as code where a real mechanism was
given (the Tumbling Inversion math, the four stage paradoxes, this one loop),
and is disclosed as reference material, not silently invented detection,
where it wasn't.
