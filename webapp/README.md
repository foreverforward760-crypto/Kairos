# Kairos Reflection Journal

A single self-contained HTML file (`pattern_reflection_journal.html`) — no build step, no server, no
dependencies. Open it directly in a browser.

## What it is

An interpretive, offline-first journaling tool — the same category as a tarot app, the I Ching, or a
structured prompt deck. You give it any text or life topic (a Bible or Quran passage, a paragraph about
a relationship, a resume bullet, a note about a recurring argument, whatever), and it reflects that text
back through the project's existing ten-stage vocabulary (`PLENARA` through `TRANSPARENCY OF THE GUIDE`)
using the same digit-root arithmetic as `engine/container_rule_engine.py` in the LASE repo.

It does **not** claim to measure or predict anything real about the text. The app says so directly, in
the UI, on first load: digit-root math finds a "pattern" in any sufficiently long input — scripture, a
grocery list, or keyboard mashing — with equal reliability. Every reading is framed as a writing prompt,
not a verdict, and the "show the math" panel on every reading exposes the exact numbers used, so nothing
is hidden.

## Micro-stage (fractal drill-down)

Every Pattern Scan reading also computes a micro-position (e.g. `4.5`) by running the exact same
word/letter digit-root formula a second time on a smaller slice of the same text — usually your closing
sentence. This mirrors the project's own canonical 81-stage structure (9 Gates × 9 micro-stages,
`docs/SAP_STAGE_CANONICAL_REFERENCE.md` §6 in LASE), where `.5` is always a threshold/pivot and `.9` is
always a transparency/release point across every Gate. The digits in between (`.1`–`.4`, `.6`–`.8`) use
one shared, generic label set rather than 81 individually-authored ones, since the source doc only
actually defines `.0`/`.5`/`.9` per Gate. It's disclosed as the same math run twice on a smaller slice,
not a more precise instrument. Cycle Journal check-ins get the same micro reading in text mode, and an
optional manual micro-position selector in self-selected mode.

## Beyond digit-root: what else is real here

The framework this app draws from is more than mod-9 arithmetic — it also has an Inversion Principle
(odd/even stage parity), a Stage 5 three-way fork (Advance/Freeze/Crisis), a Stage 8 trap-accumulation
model, and a deeper fractal resolution (81 → 729-equivalent). All four are implemented, ported from or
consistent with `engine/container_rule_engine.py` in LASE:

- **Inversion** — every reading shows physical/conscious stability per stage, straight from the engine's
  `INVERSION` table.
- **Stage 5 fork** — Stage 5 readings surface the three real directions by name, without computing the
  "probability of success" formula from the source docs, since its weights (`w1`–`w4`, `θ`) were never fit
  to real outcomes. Showing a percentage there would be invented precision, not a result — so this app
  names the three directions and lets the prompt do the work instead.
- **Trap accumulation** — the Cycle Journal flags an area when its check-ins repeat Stage 8, using the same
  consecutive-count logic (and 1.45× compounding note) as the engine's `detect_trap_accumulation`.
- **Nano-level zoom** — readings can drill a third digit deep (e.g. `4.5.2`), the same transparent formula
  run again on a smaller slice, opt-in behind a "zoom deeper" toggle.
- **Consistency signal** — the Cycle Journal computes real Shannon entropy over your own check-in history
  per life area, showing whether your self-reports cluster on one stage or scatter across many.

What's deliberately **not** here: the Stage 5 bifurcation sigmoid with its unfitted weights, and any claim
that entropy or any other feature here can distinguish "real" text from gibberish. The entropy signal
measures the consistency of a user's own repeated self-reports over time — a real, honest calculation — not
whether the content of any single entry is meaningful. That's a different (and much harder) problem that
this app doesn't attempt to solve.

## The three journals

1. **Pattern Scan** — paste any text, get a stage reading + habits + reflective prompt, save it.
2. **Cycle Journal** — name life areas (a relationship, a job search, a habit) and check in on them over
   time. Surfaces plain repeat-counts on your own entries (e.g. "Stage 8 appears in 4 of your last 6
   check-ins here") — no mystical claim, just counting what you already logged.
3. **Habit Log** — a checklist of plain-language habits per stage. Check off what you notice in
   yourself; the app tallies which stages recur most across your logs.

Plus a **Stage Guide** reference tab (not a journal) describing each stage's habits in plain language.

## Data

Everything is stored in `localStorage` in your browser only. Nothing is sent over the network. Each tab
has an export button that downloads your entries as JSON; Home has "export all" and "clear all data".

## Relationship to the rest of this project

This is a client-side companion to the `api_kairos.py` therapeutic engine in this repo — it doesn't call
the API (so it works with zero setup), but it reuses the same stage names, the same Container Rule
digit-root math, and the same "recognition over prediction" philosophy described in the main README.
