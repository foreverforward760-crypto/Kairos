"""
Kairos AI Reading Layer

Generates the AI-deepened portion of a Kairos reading: a short personalized
narrative, a real story/quote/metaphor parallel, a "Trickster Take" (a
short, funny, perspective-flipping line in the voice of one of the
project's trickster figures), and 1-2 follow-up questions -- plus a
stateless "elaborate" call that continues the thread once the reader
answers a follow-up question.

Design choices, stated plainly (no more, no less than needed):

* The *stage classification itself* is never done here -- it's already
  decided by the deterministic digit-root arithmetic (or the Bayesian
  engine, for the API-driven side of the project) before this module is
  called. This module only writes the color and depth around a stage
  that's already been named. That keeps the "the math decides, the AI
  narrates" split honest.
* Stateless by design. The caller (the browser) holds the conversation
  history and resends it -- there's no server-side reading store to keep
  in sync, back up, or leak.
* Off by default, same pattern as sap_kairos_ai_scoring.py: gated behind
  KAIROS_ENABLE_AI_READINGS and ANTHROPIC_API_KEY.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from sap_kairos_public_content import (
    TRICKSTER_VOICES,
    get_stage_handle,
    get_stage_hook,
)

READING_MODEL = os.environ.get("KAIROS_AI_READING_MODEL", "claude-sonnet-5")


class AIReadingError(Exception):
    pass


def is_ai_readings_configured() -> bool:
    return bool(
        os.environ.get("KAIROS_ENABLE_AI_READINGS", "").lower() == "true"
        and os.environ.get("ANTHROPIC_API_KEY")
    )


def _client():
    import anthropic
    return anthropic.Anthropic()


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> Dict[str, Any]:
    match = _JSON_BLOCK_RE.search(text)
    if not match:
        raise AIReadingError("Claude's response did not contain a JSON object.")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise AIReadingError(f"Claude's response was not valid JSON: {e}")


def _validate_reading_response(data: Dict[str, Any]) -> Dict[str, Any]:
    required = ["narrative", "trickster_take", "parallel", "parallel_source", "questions"]
    missing = [k for k in required if k not in data]
    if missing:
        raise AIReadingError(f"Claude's reading response is missing keys: {missing}")
    if not isinstance(data["questions"], list) or not data["questions"]:
        raise AIReadingError("Claude's reading response must include a non-empty 'questions' list.")
    return {
        "narrative": str(data["narrative"]).strip(),
        "trickster_take": str(data["trickster_take"]).strip(),
        "parallel": str(data["parallel"]).strip(),
        "parallel_source": str(data["parallel_source"]).strip(),
        "questions": [str(q).strip() for q in data["questions"][:2]],
    }


READING_SYSTEM_PROMPT = """You write for Kairos, an app where people paste a piece of text -- a journal \
entry, a passage, a description of a situation, literally anything -- and get it read through a \
ten-stage cycle. You are given the stage that's already been determined (you do not choose or \
second-guess it) and the text the reader submitted. Your job is to write the human, personalized \
layer on top of that stage: a short narrative, a real parallel (a genuine story, quote, myth, \
historical moment, or pop-culture reference -- something real, not invented, and actually apt), a \
"Trickster Take," and one or two follow-up questions.

The Trickster Take is the signature feature of this app. Write it in the voice of the given \
trickster figure (Coyote, Anansi, Loki, Br'er Rabbit, or Eshu) -- these are mythic tricksters known \
for using humor and mischief to show someone their situation from a different angle. It should be \
genuinely funny or wry, not saccharine, and it should reframe the reader's situation rather than \
just restate it. Think of it as the one line that makes someone laugh right before it makes them \
think.

Ground everything in the SPECIFIC text the reader submitted -- reference actual details from it, not \
generic stage language. Keep the tone warm, sharp, and a little playful; this is closer to a good \
tarot reader or a clever friend than a therapist's intake form. No clinical hedging, no disclaimers \
in the body text -- the app handles disclosure elsewhere.

Respond with ONLY a JSON object, no other text, in exactly this shape:
{
  "narrative": "2-4 sentences, personalized to their specific text, in plain warm language",
  "trickster_take": "1-3 sentences in the trickster's voice, funny and perspective-shifting",
  "parallel": "a real quote, story, myth, or example that genuinely parallels their situation",
  "parallel_source": "who/where the parallel is from, e.g. 'Rumi' or 'the myth of Icarus'",
  "questions": ["one or two short, specific follow-up questions to learn more about their situation"]
}"""


def generate_ai_reading(
    stage: int,
    canonical_name: str,
    text: str,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    if not is_ai_readings_configured():
        raise AIReadingError("AI readings are not enabled on this server.")

    handle = get_stage_handle(stage)
    hook = get_stage_hook(stage)
    voice = TRICKSTER_VOICES[stage % len(TRICKSTER_VOICES)]

    user_prompt = (
        f"Stage: {stage} -- \"{handle}\" (internal name: {canonical_name})\n"
        f"Stage hook: {hook}\n"
        f"Trickster voice to write in: {voice}\n"
        f"Life domain the reader tagged (may be blank): {domain or 'unspecified'}\n\n"
        f"Reader's text:\n\"\"\"\n{text[:4000]}\n\"\"\""
    )

    client = _client()
    response = client.messages.create(
        model=READING_MODEL,
        max_tokens=900,
        system=READING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(block.text for block in response.content if hasattr(block, "text"))
    data = _extract_json(raw)
    result = _validate_reading_response(data)
    result["trickster_voice"] = voice
    result["stage_handle"] = handle
    return result


ELABORATE_SYSTEM_PROMPT = """You are continuing a Kairos reading -- a short, warm, sharp reflection \
tool. The reader already got an initial reading for a fixed stage and answered a follow-up question. \
Write a short reply (2-4 sentences) that responds to what they actually said, deepens the reading \
with that new detail, and, if it's earned, adds one more specific question. Keep the same tone as \
before: warm, a little playful, no clinical hedging. Do not change or re-guess the stage.

Respond with ONLY a JSON object, no other text, in exactly this shape:
{
  "reply": "2-4 sentences responding to what they said",
  "next_question": "one more specific question, or an empty string if the thread feels complete"
}"""


def elaborate_reading(
    stage: int,
    canonical_name: str,
    original_text: str,
    thread: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Stateless continuation of a reading's follow-up thread.

    `thread` is the full prior exchange, provided by the caller each time:
    a list of {"question": ..., "answer": ...} pairs, oldest first. Nothing
    is persisted server-side.
    """
    if not is_ai_readings_configured():
        raise AIReadingError("AI readings are not enabled on this server.")
    if not thread:
        raise AIReadingError("elaborate_reading requires at least one question/answer pair.")

    handle = get_stage_handle(stage)
    thread_text = "\n".join(
        f"Q: {t.get('question', '')}\nA: {t.get('answer', '')}" for t in thread
    )
    user_prompt = (
        f"Stage: {stage} -- \"{handle}\" (internal name: {canonical_name})\n\n"
        f"Reader's original text:\n\"\"\"\n{original_text[:2000]}\n\"\"\"\n\n"
        f"Follow-up thread so far:\n{thread_text}"
    )

    client = _client()
    response = client.messages.create(
        model=READING_MODEL,
        max_tokens=500,
        system=ELABORATE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = "".join(block.text for block in response.content if hasattr(block, "text"))
    data = _extract_json(raw)
    if "reply" not in data:
        raise AIReadingError("Claude's elaborate response is missing 'reply'.")
    return {
        "reply": str(data["reply"]).strip(),
        "next_question": str(data.get("next_question", "")).strip(),
    }
