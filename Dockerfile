FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sap_kairos_geometry.py .
COPY sap_kairos_bayesian.py .
COPY sap_energy_layer.py .
COPY sap_kairos_session.py .
COPY api_kairos.py .

EXPOSE 8000

CMD ["uvicorn", "api_kairos:app", "--host", "0.0.0.0", "--port", "8000"]
