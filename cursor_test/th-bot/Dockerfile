FROM python:3.12-slim
WORKDIR /app
COPY th-bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY th-bot/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011"]
