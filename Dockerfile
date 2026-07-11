FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sap_kairos_geometry.py .
COPY sap_kairos_bayesian.py .
COPY sap_energy_layer.py .
COPY sap_kairos_session.py .
COPY sap_kairos_tumbling_inversion.py .
COPY sap_kairos_stage_paradox.py .
COPY sap_kairos_disruption_loops.py .
COPY sap_kairos_nsdt_estimator.py .
COPY sap_kairos_ai_scoring.py .
COPY sap_kairos_ai_reading.py .
COPY sap_kairos_public_content.py .
COPY api_kairos.py .

EXPOSE 8000

# Writable dir for KAIROS_STORAGE_BACKEND=file session persistence.
RUN mkdir -p /app/kairos_data

CMD ["uvicorn", "api_kairos:app", "--host", "0.0.0.0", "--port", "8000"]
