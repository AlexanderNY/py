FROM python:3.12-slim

WORKDIR /app

# Установка Chromium и зависимостей для Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    #&& rm -rf /var/lib/apt/lists/*

# Переменные для Selenium (указать путь к chromium)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# webdriver-manager может скачивать драйвер; используем системный chromedriver
# В коде можно задать options.binary_location = "/usr/bin/chromium"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
