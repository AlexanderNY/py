FROM python:3.12-slim

WORKDIR /app

COPY vk-bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared_storage /app/shared_storage
COPY vk-bot/ .

EXPOSE 8005

CMD ["python", "main.py"]
