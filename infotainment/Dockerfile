FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    dbus dbus-x11 x11-utils \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PYTHONPATH="/app"
COPY infotainment/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY infotainment/infotainment.py .
COPY infotainment/infotainment_entrypoint.sh .
COPY shared /app/shared
RUN chmod +x infotainment_entrypoint.sh
