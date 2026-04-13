# LUMINARK Kairos – Therapeutic SAP Engine

**Kairos (καιρός)** – the opportune, critical moment for change.

## Overview

Kairos is a separate engine from the industrial **LUMINARK Overwatch**. It is designed for **therapeutic, coaching, and experimental contexts** where regression, oscillation, and voluntary choice are meaningful.

- **Stage 8 → 7 regression** is allowed and interpreted as a refusal of dissolution.
- **Stage 5** is a **choice point** (kairos moment), not an irreversible boundary.
- **Outputs** include therapeutic notes, somatic invitations, trickster wisdom, coaching responses, and journal prompts.
- **Session tracking** remembers previous stages per user, detecting cynical loops (8↔7 oscillations) and regression counts.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Submit NSDT vector, get stage + therapeutic guidance |
| GET | `/history/{system_id}` | Retrieve past snapshots |
| POST | `/reset/{system_id}` | Clear session history |
| GET | `/health` | Health check |

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

## Example Response

```json
{
  "dominant_stage": 8,
  "stage_name": "False Heaven / False Hell",
  "therapeutic_note": "Stage 8 detected. Kairos invitation: 'What would it mean to let go?'",
  "somatic_invitation": "Breathe into your back body...",
  "coaching_response": "High certainty can be a trap. What would it mean to say 'I don't know'?",
  "journal_prompt": "What would you lose if you let go of the need to be certain?",
  "session": {
    "total_snapshots": 3,
    "regression_count_8_to_7": 1,
    "cynical_loop_detected": false
  }
}
```

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

## Relationship to Industrial Engine

- **Industrial (Overwatch v6.4.1)** – strict geometry, irreversible Stage 5 & 8, for infrastructure, safety, and corporate use.
- **Therapeutic (Kairos v1.0)** – forgiving, choice‑aware, for human behaviour, coaching, and healing.

Both engines share the same SAP stage ontology and NSDT input but have **different transition laws, outputs, and philosophical goals**.

## License

Proprietary – Meridian Axiom Alignment Technologies (MAAT)
