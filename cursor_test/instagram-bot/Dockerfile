FROM python:3.12-slim

WORKDIR /app

# Контекст сборки — корень репозитория (см. docker-compose: context: .)
COPY instagram-bot/requirements.txt ./requirements.txt
ENV PIP_DEFAULT_TIMEOUT=300
RUN pip install --no-cache-dir -r requirements.txt

COPY shared_storage /app/shared_storage
COPY instagram-bot/ .

EXPOSE 8011

CMD ["python", "main.py"]
