FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    dbus \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY validation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY validation/validation.py .

CMD ["python3", "validation.py"]