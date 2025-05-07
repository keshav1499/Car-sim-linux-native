FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    dbus \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ecu/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ecu/ecu.py .

CMD ["python3", "ecu.py"]