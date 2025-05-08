
# 🚗 Engine ECU Simulation using D-Bus (via Docker on WSL)

This project simulates a Mercedes-Benz style **Engine ECU** and **Validation Service** using **D-Bus**, built entirely with **Python**, and containerized using **Docker Compose**. Designed to run on **WSL (Windows Subsystem for Linux)**.

---

## 📁 Project Structure

```
car-sim/
├── docker-compose.yml
├── shared/                                   # Shared simulated D-Bus socket
│   ├── dbus-session.conf                             
├── engine-ecu/
│   ├── Dockerfile
│   ├── ecu_service.py
│   ├── requirements.txt
│   └── entrypoint.sh
└── validator/
    ├── Dockerfile
    ├── validator.py
    ├── requirements.txt
    └── entrypoint.sh
```

---

## 🧠 Components

### 1. `engine-ecu/` - Engine Control Unit (ECU) Service

- Simulates engine behavior and exposes a **D-Bus API** with methods:
  - `GetRPM`
  - `GetTemperature`
  - `FailEngine`
  - `ResetFailure`
  - `GetEngineData` (returns full status including RPM, temp, pressure, throttle)

- **Dependencies** (`requirements.txt`):
  ```
  dbus-python
  pygobject
  ```

- **Entrypoint**: Launches `dbus-daemon` and runs ECU service:
  ```bash
  #!/bin/bash
  echo "Launching D-Bus and ECU service..."
  eval `dbus-launch --sh-syntax`
  python3 ecu_service.py
  ```

- **Dockerfile**:
  ```Dockerfile
  FROM python:3.11-slim

  RUN apt update && apt install -y \
      libdbus-1-dev libglib2.0-dev dbus-x11 \
      python3-gi python3-dbus gir1.2-glib-2.0

  WORKDIR /app
  COPY . /app

  RUN pip install -r requirements.txt
  ENTRYPOINT ["./entrypoint.sh"]
  ```

---

### 2. `validator/` - Data Checker Client

- Connects to the ECU service using **asynchronous D-Bus (dbus-next)**.
- Periodically pulls and validates engine data: RPM, Speed, Coolant Temp, Oil Pressure, Throttle Position.
- Displays table output and flags dangerous conditions with warnings.

- **Dependencies** (`requirements.txt`):
  ```
  dbus-next
  tabulate
  ```

- **Entrypoint**:
  ```bash
  #!/bin/bash
  echo "Launching Validator..."
  eval `dbus-launch --sh-syntax`
  python3 validator.py
  ```

- **Dockerfile**:
  ```Dockerfile
  FROM python:3.11-slim

  RUN apt update && apt install -y \
      libdbus-1-dev dbus-x11

  WORKDIR /app
  COPY . /app

  RUN pip install -r requirements.txt
  ENTRYPOINT ["./entrypoint.sh"]
  ```

---

## 🐳 docker-compose.yml

```yaml
version: '3.8'

services:
  ecu:
    build: ./engine-ecu
    container_name: engine-ecu
    environment:
      - DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus.sock
    volumes:
      - ./dbus:/tmp

  validator:
    build: ./validator
    container_name: ecu-validator
    depends_on:
      - ecu
    environment:
      - DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus.sock
    volumes:
      - ./dbus:/tmp
```

---

## ⚙️ Setup Instructions (WSL)

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd car-sim
```

### 2. Ensure WSL Setup
- Use Ubuntu in WSL2 (Ubuntu 20.04+)
- Ensure Docker Desktop is installed and **WSL integration** is enabled
- Test Docker access:
  ```bash
  docker --version
  docker-compose --version
  ```

### 3. Create Shared D-Bus Volume
```bash
mkdir -p dbus
```

### 4. Build and Launch Containers
```bash
docker-compose build
docker-compose up
```

Output from ECU and validator services will print on terminal.

---

## 🔍 Troubleshooting

### ❗ pygobject fails to build?
Ensure the following packages are present in the Dockerfile:
```Dockerfile
libdbus-1-dev libglib2.0-dev dbus-x11 python3-gi python3-dbus gir1.2-glib-2.0
```

### ❗ `girepository-2.0` missing?
Install: `libgirepository1.0-dev` (note: not available on Alpine or minimal distros).

---

## 📦 Optional Improvements
- Use `tabulate` for cleaner terminal output in `validator.py`.
- Use `colorama` or `rich` for color-coded status.

---

## 🗓️ Last Updated
May 08, 2025
