FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps

COPY . .

# Los PDFs se montan aquí en tiempo de ejecución
VOLUME ["/app/data"]

ENTRYPOINT ["python", "run.py"]
