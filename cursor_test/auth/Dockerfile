FROM python:3.12-slim
WORKDIR .
RUN apt-get update \
    && apt-get install -y curl jq
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "172.20.10.1", "--port", "8001"]
