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
