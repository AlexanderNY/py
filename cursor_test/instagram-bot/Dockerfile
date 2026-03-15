FROM python:3.12-slim

WORKDIR /app

COPY instagram-bot/requirements.txt .
ENV PIP_DEFAULT_TIMEOUT=300
RUN pip install --no-cache-dir -r requirements.txt

COPY shared_storage /app/shared_storage
COPY instagram-bot/ .

EXPOSE 8012

CMD ["python", "main.py"]
