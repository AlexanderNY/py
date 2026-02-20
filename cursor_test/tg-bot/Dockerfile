FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Директории для сессий Telethon и загрузок
RUN mkdir -p sessions uploads/tg

EXPOSE 8004

CMD ["python", "main.py"]
