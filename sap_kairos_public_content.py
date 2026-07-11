"""
Kairos Public Content Layer

Consumer-facing vocabulary for the Kairos ten-stage cycle. This module holds
no math -- it is a naming/framing layer on top of the existing engine
(sap_kairos_geometry.py / sap_kairos_bayesian.py / the webapp's own
digit-root arithmetic). Canonical internal names (PLENARA, VESSEL OF
GROUNDING, etc.) are preserved everywhere else in the project; this module
gives each stage a short, plain-language "handle" for a general audience,
the same way a tarot deck has a formal card name ("The Hanged Man") and a
short read on what it means.

Nothing here changes stage classification. It only changes what a reader
sees.
"""

from typing import Dict

# short public handle + one-line hook per stage, keyed to the canonical
# stage index used throughout the project (0-9)
STAGE_HANDLES: Dict[int, Dict[str, str]] = {
    0: {"handle": "The Open Field", "hook": "The pause before the next thing starts."},
    1: {"handle": "The Spark", "hook": "An idea that won't leave you alone yet."},
    2: {"handle": "The Divide", "hook": "Finding yourself by finding what you're not."},
    3: {"handle": "The Push", "hook": "Momentum, on repeat, sometimes outrunning reflection."},
    4: {"handle": "The Steady", "hook": "Standing on ground that feels solid -- for now."},
    5: {"handle": "The Turn", "hook": "The fork in the road. This is the actual kairos moment."},
    6: {"handle": "The Weave", "hook": "Pulling separate threads back into one picture."},
    7: {"handle": "The Clarity", "hook": "Seeing it clearly -- maybe alone."},
    8: {"handle": "The Grip", "hook": "Holding on to something as if letting go would be worse."},
    9: {"handle": "The Release", "hook": "Setting it down. The turn back toward the Open Field."},
}

# public names for the two Stage 8 sub-readings (see sap_kairos_geometry.py
# STAGE8_CHAMBER_ARRIVAL / STAGE8_CHAMBER_PERMANENCE for the canonical pair)
CHAMBER_PUBLIC_NAMES: Dict[str, str] = {
    "Illusion of Arrival": "The High Grip -- gripping a peak, convinced it's permanent.",
    "Illusion of Permanence": "The Low Grip -- gripping a low point, convinced it's permanent.",
}

# The 0-9-0 Tumbling Inversion, explained once, plainly, for reuse in
# whatever surface needs a short version.
TUMBLING_INVERSION_SHORT = (
    "Kairos treats the ten stages as a loop, not a ladder: 0 through 9 and "
    "back to 0. Climbing and falling are the same motion seen from different "
    "sides -- a full turn, not a finish line. Nobody is ever only in one "
    "stage; the reading names where the weight currently sits."
)

# Short, honest, non-clinical data note. Not an "offline-only" promise --
# the AI-deepened reading (when a reader opts into it) sends their text to
# Anthropic's Claude API to generate it. This explains that plainly instead
# of overstating privacy either direction.
DATA_HANDLING_NOTE = (
    "The base reading (the stage, the habits, the quote) runs entirely on "
    "your device using simple word/letter arithmetic -- nothing is sent "
    "anywhere for that part. If you tap \"Ask Kairos to go deeper,\" the "
    "text you're reading gets sent to Claude (Anthropic's AI) to generate "
    "a personalized narrative, a story parallel, and follow-up questions. "
    "That request isn't used to train anything, but as with anything you "
    "type into any online tool: don't paste something here you wouldn't "
    "want to leave your device, and use the same judgment you'd use "
    "anywhere else online."
)

TRICKSTER_VOICES = [
    "Coyote", "Anansi", "Loki", "Br'er Rabbit", "Eshu",
]


def get_stage_handle(stage: int) -> str:
    return STAGE_HANDLES.get(stage, {}).get("handle", f"Stage {stage}")


def get_stage_hook(stage: int) -> str:
    return STAGE_HANDLES.get(stage, {}).get("hook", "")


def get_public_chamber_name(chamber: str) -> str:
    return CHAMBER_PUBLIC_NAMES.get(chamber, chamber)
