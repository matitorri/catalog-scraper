FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Los PDFs se montan aquí en tiempo de ejecución
VOLUME ["/data"]

ENTRYPOINT ["python", "run.py"]
