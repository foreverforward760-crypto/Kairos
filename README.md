# LUMINARK Kairos – Therapeutic SAPP Engine

**Kairos (καιρός)** – the opportune, critical moment for change.

> **Framework:** Stanfield's Axiom of **Perceived** Perpetuity (SAPP)  
> **Governing Doctrine:** See `SAPP_OPERATIONAL_DOCTRINE.md` in LASE  
> **Version:** Kairos v1.0 | Engine Build: `build2_kairos` | Port: 8002

---

## Architectural Position

Kairos is the **therapeutic build** of the SAPP engine. It operates entirely within **Layer Two — The Experiential Relative**: the fragmented, sequential arc as lived by a conscious being equipped with a Stage 5 perceptual apparatus.

The cosmological foundation of SAPP (the 0-9-0 as a single simultaneous event) is not suspended in the therapeutic context — it is the most powerful resource available to it. A client in Stage 8 Perceived Permanence — experiencing their current state as eternal, fixed, and inescapable — is not stuck in a sequence that has no exit. They are at a position on a torus that simultaneously contains its own release. The ascending arc is not ahead of them. It is already present in the same moment as the descent. Kairos outputs this truth, not as comfort, but as geometry.

---

## Overview

Kairos is a separate engine from the industrial **LUMINARK Overwatch**. It is designed for **therapeutic, coaching, and experimental contexts** where regression, oscillation, and the lived experience of threshold crossing are meaningful.

- **Stage 8 → 7 regression** is allowed and interpreted as a refusal of dissolution — not failure, but a classifiable state with its own guidance.
- **Stage 5** is a **threshold state** (the kairos moment): all possibilities simultaneously present, none yet committed. Resolution occurs through structural resonance — what the person is aligned with at depth — not through deliberate intellectual decision. Coaching at Stage 5 does not say "you can choose." It says: "the threshold resolves through what you are." The Kairos moment is not a fork in a road. It is the prism being entered.
- **Outputs** include therapeutic notes, somatic invitations, trickster wisdom, coaching responses, and journal prompts — all calibrated to the Tumbling Inversion: descent and ascent are the same motion on the same surface, perceived as two directions.
- **Session tracking** remembers previous stages per client, detecting cynical loops (8↔7 oscillations) and regression counts.

---

## Constitutional Constraints (Non-Negotiable)

### Canonical Stage 8 Language

Stage 8 is **VESSEL OF GROUNDING**. Its two chambers are:

| Chamber | Name | Description |
|---------|------|-------------|
| A | **Illusion of Arrival** | High-frequency trap — the belief that a permanent blissful or righteous state has been achieved |
| B | **Illusion of Permanence** | Low-frequency trap — the belief that the current state of suffering or stagnation will never end |

The construct is the **Stage 8 Dual-Chamber Trap**. TrapScore amplifier: **1.45×**.

> ⛔ **Deprecated — Never Use:** `False Heaven`, `False Hell`, `FALSE_HEAVEN`, `FALSE_HELL`, `F-HELL`, or any variant. These terms are constitutionally prohibited across the entire SAPP ecosystem.

### Canonical Stage Names

All stages must use exact canonical names. No abbreviations, truncations, or alterations.

| Stage | Canonical Name |
|-------|----------------|
| 0 | PLENARA |
| 1 | SPARK OF NAVIGATION |
| 2 | FORGE OF POLARITY |
| 3 | ENGINE OF EXPRESSION |
| 4 | CRUCIBLE OF EQUILIBRIUM |
| 5 | DYNAMO OF WILL |
| 6 | NEXUS OF HARMONY |
| 7 | LENS OF DISTILLATION |
| 8 | VESSEL OF GROUNDING |
| 9 | TRANSPARENCY OF THE GUIDE |

### Tumbling Inversion — Therapeutic Application

Descent and ascent are not sequential. They are the same motion happening simultaneously on the same torus surface. This is not a metaphor offered to clients as hope. It is the geometric fact that governs every therapeutic output Kairos produces.

- A client at Stage 8 Chamber B (Illusion of Permanence) is not at the farthest point from release. They are at the Inversion Point. The release is structurally co-present.
- Coaching outputs must not imply that the client must "get through" Stage 8 before something better can begin. The better is simultaneous with the current. The geometry is the intervention.

---

## The Tumbling Inversion engine is real code, not copy

Every `/analyze` and `/reading` response includes a `tumbling_inversion` block. This is not
descriptive language layered on top of a reading — it's the actual Tumbling Inversion Principle
(Stanfield's Axiom of Perceived Perpetuity / `TUMBLING_INVERSION_v8.2.md`) running as deterministic
code against the NSDT vector for that reading, ported from and verified against the user's own
`tumbling_inversion.py` and `test_tumbling_inversion.py` (all 25 of the original tests pass
unmodified against this implementation — see `sap_kairos_tumbling_inversion.py`).

| Field | What it is |
|---|---|
| `parity` | `even` / `odd` / `boundary` — even stages (2,4,6,8) are Physically Stable / Consciously Unstable; odd stages (1,3,5,7,9) are Physically Unstable / Consciously Stable. This alternation is the mechanism of forward motion, not a flaw — picture a cylinder rolling down a slope, alternating between resting on a face and tumbling over its edge. |
| `physical_stability`, `consciousness_stability` | 0–100, computed from the NSDT vector (see `docs/NSDT_REFERENCE.md`). |
| `divergence`, `divergence_category` | Gap between the Revealed Self (projected stability) and the Concealed Self (actual tension carried) — the same gap the Stage 8 Gratitude Mechanism exists to close. |
| `geometric_form` | The stage's canonical geometric form (Point, Line, Triangle, Square, Perpendicular Axis, Hexagon, Heptagon, Octagon, Nonagon, Circle). |
| `arc_direction`, `arc_confidence` | `ascending` / `descending` / `plateau` / `indeterminate`, computed from recent NSDT history on the session (`< 2` history points is always `indeterminate`). |
| `middle_path_accessed`, `witness_score` | Stage 5's Middle Path Gateway (`witness_score > 50`). **Sticky on the session once accessed** — per the framework's own claim, a conscious choice at Stage 5 reorganizes every remaining stage in that session's cycle, not just the moment it happens. |
| `stage_paradox` | Populated only at Stages 6, 7, 8 — the Conductor's Paradox (Sustainable vs. Brittle Flow), the Individuation Crucible (Conscious Distillation vs. Chaotic Collapse, plus shadow-surfacing detection), or the Crystallization Paradox (the Gratitude Mechanism engaging or Shattering). |
| `disruption_loop` | Populated when the existing 8→7→8 / repeated-alternation detector fires — maps to the **Wrath** Stage Disruption Loop. See `docs/STAGE_DISRUPTION_LOOPS.md` for all seven (Pride, Greed, Lust, Envy, Gluttony, Wrath, Sloth), ported from the SAPP corpus's reframing of the Seven Deadly Sins as self-perpetuating stage loops with an "ascending antidote" each. |

For `/reading` (the consumer AI reading), the NSDT vector isn't submitted directly — it's estimated
by Claude from the reader's own text (`sap_kairos_nsdt_estimator.py`), kept blind to stage names and
Tumbling Inversion thresholds so it can't reverse-engineer a "convenient" vector, then run through
the exact same engine as `/analyze`. The AI-generated narrative is then written *on top of* that
real computed state (see `generate_ai_reading()` in `sap_kairos_ai_reading.py`) — Claude explains
what the math found, it doesn't invent its own version of it.

See [`docs/NSDT_REFERENCE.md`](docs/NSDT_REFERENCE.md) for the confirmed axis definitions (and a
documented, real inconsistency: the *stage classifier* that picks `dominant_stage` still runs on an
older, unconfirmed axis guess — read that doc before assuming every field in a response carries the
same confidence).

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Submit NSDT vector, get stage + therapeutic guidance |
| GET | `/history/{system_id}` | Retrieve past snapshots |
| POST | `/reset/{system_id}` | Clear session history |
| POST | `/score-nsdt` | AI-assisted NSDT scoring from freeform notes (opt-in, see below) |
| POST | `/reading` | AI-deepened consumer reading: narrative, story parallel, Trickster Take, follow-up questions (opt-in, see below) |
| POST | `/reading/elaborate` | Continue a reading's follow-up thread (stateless, opt-in, see below) |
| GET | `/health` | Health check |

---

> See [`docs/NSDT_REFERENCE.md`](docs/NSDT_REFERENCE.md) for what the 5-element `nsdt` vector means, including
> which parts are confirmed by code vs. best-effort inference that still needs sign-off, and
> [`docs/STAGE_DISRUPTION_LOOPS.md`](docs/STAGE_DISRUPTION_LOOPS.md) for the seven Stage Disruption Loops
> referenced by the `disruption_loop` field below.

## Example Request

```bash
curl -X POST http://localhost:8002/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": "client_001",
    "nsdt": [6.2, 4.5, 7.8, 3.2, 5.1],
    "allow_regression": true,
    "journal_entry": "I feel stuck and scared."
  }'
```

---

## Example Response

```json
{
  "dominant_stage": 8,
  "stage_name": "VESSEL OF GROUNDING",
  "chamber": "Illusion of Permanence",
  "trap_score_amplifier": 1.45,
  "therapeutic_note": "Stage 8 — VESSEL OF GROUNDING detected. The state you are experiencing as permanent is a position on a torus that simultaneously contains its own release. The ascending arc is not ahead of you. It is already present in the same moment as what you feel now.",
  "somatic_invitation": "Breathe into your back body. Notice what has not changed while this feeling has been present.",
  "coaching_response": "The certainty that this will not end is itself the trap — not your suffering, but your conclusion about its duration. What would it mean to hold the feeling without the verdict?",
  "journal_prompt": "What would you lose if you let go of the need to know how long this lasts?",
  "tumbling_inversion_note": "Descent and ascent are the same motion. You are not waiting for the return arc. You are already on it.",
  "tumbling_inversion": {
    "parity": "even",
    "physical_stability": 71.0,
    "consciousness_stability": 75.0,
    "divergence": 30.0,
    "divergence_category": "moderate",
    "geometric_form": "Octagon",
    "arc_direction": "ascending",
    "arc_confidence": 62.5,
    "middle_path_accessed": true,
    "witness_score": 58.0,
    "stage_paradox": {
      "trajectory": "dissolution",
      "gratitude_engaged": true,
      "directive": "..."
    },
    "disruption_loop": null
  },
  "session": {
    "total_snapshots": 3,
    "regression_count_8_to_7": 1,
    "cynical_loop_detected": false
  }
}
```

`tumbling_inversion` is the real, computed engine output — see "The Tumbling Inversion engine is
real code, not copy" above for what each field means.

`chamber` and `trap_score_amplifier` are only populated when `dominant_stage == 8` (`null` otherwise). Chamber
classification is a first-pass, disclosed heuristic — see the docstring on `classify_stage8_chamber()` in
`sap_kairos_geometry.py` and `docs/NSDT_REFERENCE.md` before relying on it clinically.

---

## Configuration

All optional, read from the environment at startup:

| Variable | Default | Purpose |
|---|---|---|
| `KAIROS_STORAGE_BACKEND` | `memory` | `memory` or `file`. `memory` sessions do not survive a restart and are not shared across multiple uvicorn workers — use `file` for anything beyond local single-process dev. |
| `KAIROS_DATA_DIR` | `./kairos_data` | Directory for per-client session JSON when `KAIROS_STORAGE_BACKEND=file`. `system_id` is sanitized before being used in a filename, so this is safe against path traversal even with untrusted `system_id` input. |
| `KAIROS_API_KEY` | unset | If set, every request except `/health` must send a matching `X-API-Key` header. If unset, the API is open — fine for local dev, not for anything network-reachable. |
| `KAIROS_ALLOWED_ORIGINS` | unset | Comma-separated origins allowed to call this API from a browser (CORS). If unset, no CORS middleware is added at all — the safe default is that no browser can call this cross-origin. |
| `KAIROS_ENABLE_AI_READINGS` | unset | `true` to turn on `POST /reading` and `POST /reading/elaborate` (see "Kairos App" section below). |
| `KAIROS_AI_READING_MODEL` | `claude-sonnet-5` | Claude model used for `/reading` and `/reading/elaborate`. |

## AI-Assisted NSDT Scoring (optional)

`POST /score-nsdt` sends freeform session notes to Claude and gets back a *proposed* 5-axis NSDT
vector with per-axis reasoning, a confidence label, and caveats — not a finished score. The
practitioner reviews and adjusts it, then submits it to `/analyze` themselves; nothing in this
path auto-submits anything.

Two deliberate design choices:

- **Off by default, one server-level switch.** The endpoint returns `503` unless the operator sets
  both `KAIROS_ENABLE_AI_SCORING=true` and `ANTHROPIC_API_KEY`. There's no per-request flag —
  turning this on is a decision for whoever runs the server, made once, not something a client can
  opt into per call.
- **Claude never sees the stage taxonomy.** The prompt (see `sap_kairos_ai_scoring.py`) only
  contains the five axis definitions from `docs/NSDT_REFERENCE.md` — not `STAGE_CENTROIDS`, stage
  names, or chamber logic. This keeps scoring (reading the notes) and classification (the
  deterministic geometry engine) separate, so Claude can't reverse-engineer a "convenient" vector
  from knowing what stage it would produce.

```bash
curl -X POST http://localhost:8002/score-nsdt \
  -H "Content-Type: application/json" \
  -d '{"notes": "Client kept saying '\''this is just how it is now'\'', resisted any reframe.", "system_id": "client_001"}'
```

Additional env vars: `KAIROS_ENABLE_AI_SCORING`, `ANTHROPIC_API_KEY`, and optionally
`KAIROS_AI_SCORING_MODEL` (defaults to `claude-sonnet-5`). Since notes sent here leave your server
and go to Anthropic's API, only enable this if that's acceptable for your data — same principle as
any other third-party API call with client data in it.

Example production-leaning run:

```bash
KAIROS_STORAGE_BACKEND=file \
KAIROS_DATA_DIR=/var/lib/kairos \
KAIROS_API_KEY=$(openssl rand -hex 32) \
uvicorn api_kairos:app --host 0.0.0.0 --port 8000
```

---

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn api_kairos:app --host 0.0.0.0 --port 8002

# Or use Docker
docker build -t luminark-kairos .
docker run -p 8002:8000 luminark-kairos
```

---

## Relationship to Industrial Engine

| | Industrial (LASE / Overwatch) | Therapeutic (Kairos) |
|---|---|---|
| Stage 5 | Irreversible boundary — cascade consequences | Threshold state — structural resonance, not deliberate choice |
| Stage 8 | Strict geometry, TrapScore 1.45× amplifier | Forgiving; regression to Stage 7 allowed and classified |
| Output | Carrier risk advisories, grid stress alerts, infrastructure signals | Therapeutic notes, somatic invitations, journal prompts, coaching |
| User | Infrastructure operators, logistics brokers, safety systems | Therapists, coaches, individuals in conscious arc navigation |
| Philosophy | Consequence and prediction | Recognition and release |

Both engines share the same SAPP stage ontology, NSDT input schema, and Tumbling Inversion geometry. They have different transition laws, outputs, and operational goals. Neither supersedes the other.

---

## Reflection Journal (Web App)

`webapp/pattern_reflection_journal.html` is a self-contained, offline-first companion app — open the file
directly in a browser, no server or build step required. It's framed honestly as an interpretive
journaling tool (the same category as tarot or the I Ching), not a predictive or diagnostic one: it takes
any text or life topic — ancient/sacred text, a relationship, work, diet, an emotional trigger, anything —
and reflects it through the stage vocabulary above using the same Container Rule digit-root math as
`engine/container_rule_engine.py` in LASE, with the math shown transparently on every reading.

It ships three journals — **Pattern Scan** (scan any text/topic and save the reading), **Cycle Journal**
(track named life areas over time and surface repeat-stage patterns in your own check-ins), and **Habit
Log** (a per-stage habit checklist that tallies what recurs) — plus a **Stage Guide** reference tab. All
data stays in the browser's local storage. See `webapp/README.md` for details.

---

## Kairos App (`webapp/kairos_app.html`) — consumer build

`webapp/kairos_app.html` is the same Reflection Journal, with an optional AI-deepened reading layer built
on top of it. It's aimed at a general reader, not a practitioner: paste anything (a passage, a journal
entry, a description of a situation) and it names the stage, then — if you want more — asks Claude to
write a personalized narrative, pull a real story or quote that parallels your situation, and hand you a
**Trickster Take**.

**Trickster Take** is the app's signature bit: a short, wry line written in the voice of one of five
mythic tricksters (Coyote, Anansi, Loki, Br'er Rabbit, Eshu) that reframes your situation instead of just
restating it — closer to a sharp friend or a good tarot reader than a clinical readout. The base engine
already had one fixed trickster line per stage (`sap_kairos_geometry.py`); this generates a fresh one
every time, grounded in what you actually wrote.

Other additions on top of the base journal:

- **"Ask Kairos to go deeper"** — one tap on any reading sends the stage (already decided by the local
  digit-root math -- that entry mechanic stays as-is, it's the game) and your text to `POST /reading`.
  The backend estimates an NSDT vector from your text and runs it through the real Tumbling Inversion
  engine (same math as `/analyze` -- see "The Tumbling Inversion engine is real code, not copy" above),
  then writes the narrative, Trickster Take, story/quote parallel, and 1-2 follow-up questions grounded
  in that real computed state, not invented independently of it.
- **Follow-up thread** — tapping a follow-up question opens a short reply box; your answer goes to
  `POST /reading/elaborate` along with the thread so far, and Kairos responds in place. Nothing is stored
  server-side — the browser holds the thread and resends it each time.
- **Share card** — turns a reading into a downloadable image (stage, one-line Trickster Take, no personal
  text) sized for sharing.
- **Streak** — counts consecutive days with any journal activity across all three journals.
- **Fully optional, off by default** — with no backend connected, the app behaves exactly like
  `pattern_reflection_journal.html`: local-only, no network calls. Connecting it (Home tab → "Kairos AI")
  just means pointing the page at a running `api_kairos.py` with `KAIROS_ENABLE_AI_READINGS=true` set.

### What actually happens to what you share

The base reading never leaves the device — it's word/letter arithmetic run in the browser. The moment you
tap "Ask Kairos to go deeper" or answer a follow-up question, that text is sent to the backend and on to
Anthropic's Claude API to generate the response. It isn't used to train anything, but the honest framing
is the same one that applies to any online tool: don't paste something you wouldn't want to leave your
device, and use the same judgment here you'd use anywhere else online. This is stated in-app, not just
here.

### Public stage names

`kairos_app.html` keeps the same canonical internal stage names as the rest of the project
(`sap_kairos_public_content.py` is the naming layer, nothing else changes), but gives each stage a short
public handle for quick scanning:

| Stage | Canonical name | Public handle |
|---|---|---|
| 0 | PLENARA | The Open Field |
| 1 | SPARK OF NAVIGATION | The Spark |
| 2 | FORGE OF POLARITY | The Divide |
| 3 | ENGINE OF EXPRESSION | The Push |
| 4 | CRUCIBLE OF EQUILIBRIUM | The Steady |
| 5 | DYNAMO OF WILL | The Turn |
| 6 | NEXUS OF HARMONY | The Weave |
| 7 | LENS OF DISTILLATION | The Clarity |
| 8 | VESSEL OF GROUNDING | The Grip |
| 9 | TRANSPARENCY OF THE GUIDE | The Release |

The 0-9-0 Tumbling Inversion is unchanged and still the app's core explanatory device: the ten stages are
a loop, not a ladder — descending and ascending are the same motion seen from different sides, and nobody
is ever in only one stage at a time. `TUMBLING_INVERSION_SHORT` in `sap_kairos_public_content.py` has the
one-paragraph version used in-app.

### Running it

```bash
KAIROS_ENABLE_AI_READINGS=true ANTHROPIC_API_KEY=sk-ant-... KAIROS_ALLOWED_ORIGINS=https://your-frontend-host uvicorn api_kairos:app --host 0.0.0.0 --port 8000
```

Then open `webapp/kairos_app.html` (as a local file, or hosted anywhere static), go to the Home tab →
Kairos AI, and paste the backend's address.

**Note for public deployment:** `/reading` and `/reading/elaborate` are intentionally *not* behind
`KAIROS_API_KEY` — they're meant to be called directly from a public browser page with no login. That
also means anyone who finds the URL can call them and spend your Anthropic budget. If you deploy this
publicly, put it behind a reverse proxy with rate limiting (or your own lightweight per-IP throttle) before
it's reachable from the internet — that's infrastructure this repo doesn't provide.

---

## API vs. Reflection Journal — Independent Classifiers

`api_kairos.py` (Bayesian, NSDT-driven) and `webapp/pattern_reflection_journal.html` (digit-root arithmetic on
pasted text) are two independent, intentionally separate ways of arriving at a stage. They share the same stage
names and Tumbling Inversion vocabulary but not the same math, and **can disagree** — a client's `nsdt` vector
might classify as Stage 5 in the API while the same client's journal text digit-roots to Stage 7 in the web app.
That's expected, not a bug: one method reads structured clinical input, the other reads text through a
transparent, disclosed arithmetic lens (see `webapp/README.md`). Don't treat one as a check on the other unless
you're deliberately comparing them.

---

## Governing Doctrine Reference

This engine is governed by the **SAPP Operational Doctrine** (see LASE: `docs/SAPP_OPERATIONAL_DOCTRINE.md`). Kairos operates entirely within Layer Two — the Experiential Relative — and addresses Category A systems: conscious beings with Stage 5 perceptual apparatus for whom free will, threshold crossing, and the fragmented arc are lived realities with material consequence.

---

## License

Proprietary – Meridian Axiom Alignment Technologies (MAAT)  
© 2026 Richard L. Stanfield. All rights reserved.  
Stanfield's Axiom of Perceived Perpetuity (SAPP) is proprietary intellectual property of Richard L. Stanfield / MAAT.
