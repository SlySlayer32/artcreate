FROM python:3.11-slim

WORKDIR /app

COPY services/document-intelligence/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/document-intelligence/app ./app
COPY shared ./shared
COPY ai ./ai

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
