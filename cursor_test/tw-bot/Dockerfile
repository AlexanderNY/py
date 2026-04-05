FROM python:3.12-slim

WORKDIR /app

COPY tw-bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tw-bot/ .

EXPOSE 8011

CMD ["python", "main.py"]
