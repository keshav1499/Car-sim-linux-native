FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    dbus dbus-x11 x11-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH="/app"

# Install Python dependencies
COPY validation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy validation script and entrypoint
COPY validation/validation.py .
COPY validation/validator_entrypoint.sh .
COPY shared /app/shared
RUN chmod +x validator_entrypoint.sh

