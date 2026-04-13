"""
LUMINARK Kairos Engine v1.0 – Therapeutic API with session tracking, journaling, and coaching.
Kairos: the opportune moment for change.
"""

import os
import time
import math
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional
from dataclasses import asdict

from sap_kairos_bayesian import KairosBayesian
from sap_kairos_session import KairosSession, KairosSnapshot

app = FastAPI(title="LUMINARK Kairos Engine", version="1.0")

_sessions: dict[str, KairosSession] = {}

class KairosInput(BaseModel):
    system_id: str
    nsdt: list[float] = Field(..., min_items=5, max_items=5)
    allow_regression: bool = True
    temperature: float = 0.7
    beta: float = 0.6
    journal_entry: Optional[str] = None

    @validator('nsdt')
    def validate_nsdt(cls, v):
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"nsdt[{i}] must be a number")
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"nsdt[{i}] is NaN or Inf")
            if val < 0.0 or val > 10.0:
                raise ValueError(f"nsdt[{i}] out of range 0-10")
        return v

def get_or_create_session(system_id: str) -> KairosSession:
    if system_id not in _sessions:
        _sessions[system_id] = KairosSession(system_id, storage_backend="memory")
    return _sessions[system_id]

def generate_coaching_response(stage: int, trap_energy: float, journal_entry: Optional[str]) -> str:
    if journal_entry:
        jl = journal_entry.lower()
        if "stuck" in jl or "can't move" in jl:
            return "It sounds like you feel stuck. Stage progression can feel slow – that's normal. What would one small step look like?"
        if "scared" in jl or "fear" in jl:
            return "Fear is a signal, not a stop sign. At Stage 5, fear often means you care. What is the smallest risk you could take today?"
        if "angry" in jl:
            return "Anger often masks grief or unmet need. Can you feel what is underneath?"
    if stage == 8:
        if trap_energy > 0.7:
            return "High certainty can be a trap. What would it mean to say 'I don't know'?"
        return "Stage 8 invites you to question your own mastery. Who would you be without the story of having arrived?"
    if stage == 7:
        return "Insight without connection can become isolation. Can you share what you're learning with one trusted person?"
    if stage == 5:
        return "You are at a kairos moment. No decision is permanent – but indecision is also a choice. What feels most alive?"
    return "Trust the process. The stage you are in is exactly where you need to be."

@app.post("/analyze")
def analyze_kairos(inp: KairosInput):
    engine = KairosBayesian(
        temperature=inp.temperature,
        beta=inp.beta,
        allow_regression=inp.allow_regression
    )
    session = get_or_create_session(inp.system_id)
    prev = session.get_previous_stage()
    if prev is not None:
        engine.previous_stage = prev

    x = np.array(inp.nsdt)
    result = engine.forward(x)

    snapshot = KairosSnapshot(
        timestamp=time.time(),
        dominant_stage=result["dominant_stage"],
        expected_stage=result["expected_stage"],
        entropy=result["entropy"],
        trap_energy=result["trap_energy"],
        therapeutic_note=result["therapeutic_note"],
        somatic_invitation=result["somatic_invitation"],
        trickster_wisdom=result["trickster_wisdom"],
    )
    session.add_snapshot(snapshot)

    regression_count = session.get_regression_count()
    cynical_loop = session.detect_cynical_loop()
    coaching = generate_coaching_response(result["dominant_stage"], result["trap_energy"], inp.journal_entry)

    journal_prompt = None
    if result["dominant_stage"] == 8:
        journal_prompt = "What would you lose if you let go of the need to be certain?"
    elif result["dominant_stage"] == 7:
        journal_prompt = "What insight feels too heavy to share? Who could you share it with?"
    elif result["dominant_stage"] == 5:
        journal_prompt = "What is the decision you are avoiding? What would you choose if you knew you couldn't fail?"

    result.update({
        "system_id": inp.system_id,
        "session": {
            "total_snapshots": len(session.snapshots),
            "regression_count_8_to_7": regression_count,
            "cynical_loop_detected": cynical_loop,
        },
        "coaching_response": coaching,
        "journal_prompt": journal_prompt,
    })
    return result

@app.get("/history/{system_id}")
def get_history(system_id: str, limit: int = 20):
    session = get_or_create_session(system_id)
    history = session.get_history(limit)
    return {"system_id": system_id, "history": [asdict(s) for s in history]}

@app.post("/reset/{system_id}")
def reset_session(system_id: str):
    if system_id in _sessions:
        del _sessions[system_id]
    return {"status": "reset", "system_id": system_id}

@app.get("/health")
def health():
    return {"status": "ok", "engine": "LUMINARK Kairos", "active_sessions": len(_sessions)}
