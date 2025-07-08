FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    dbus dbus-x11 x11-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH="/app"

# Install Python dependencies
COPY ecu/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ECU script and entrypoint
COPY ecu/ecu.py .
COPY ecu/ecu_entrypoint.sh .
# 👇 Copy the shared module directly into /app/
COPY shared /app/shared

RUN chmod +x ecu_entrypoint.sh

# Don't define CMD here — docker-compose overrides it with entrypoint script

