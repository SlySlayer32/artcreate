FROM python:3.11-slim

WORKDIR /app

COPY services/api-gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/api-gateway/app ./app
COPY shared ./shared

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
