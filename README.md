
# 🚗 car-sim — Linux-native D-Bus ECU Simulation

Simulate an automotive Engine Control Unit (ECU) and a Validator module communicating over **D-Bus**, using **Python**, **Docker**, and **asyncio**.

This project reflects modern **service-oriented automotive software architectures**, such as those in **AUTOSAR Adaptive**, **MB.OS**, or **AGL (Automotive Grade Linux)**.

---

## 📦 Features

- 🧠 Simulated **Engine ECU** with realistic, random automotive telemetry:
  - RPM, Speed, Coolant Temp, Oil Pressure, Throttle Position
- 🔁 D-Bus-based inter-process communication
- 🧪 Validation service that fetches ECU values at regular intervals
- 🐳 Docker-native environment using `docker-compose`
- 🛠️ Cross-platform but optimized for **Linux native development** (not WSL)

---

## 🧰 Requirements

- Docker
- Docker Compose v2
- Linux OS (Fedora, Ubuntu, Debian, Arch, etc.)
- SELinux (Fedora users may need volume labeling via `:Z`)

---

## 🗂️ Directory Structure

```
car-sim/
├── docker-compose.yml
├── shared/                         # Shared D-Bus config
│   |── dbus-session.conf
|   |── __init__.py
|   |── signal_definitions.py
|   └── DTC_definitions.py
├── docker-tmp/                     # Shared /tmp volume for dbus.sock
├── ecu/
│   ├── ecu.py                      # ECU simulator
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ecu_entrypoint.sh
├── validation/
│   ├── validation.py               # Validator service
│   ├── requirements.txt
│   ├── Dockerfile
│   └── validator_entrypoint.sh
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/car-sim.git
cd car-sim
```

### 2. Ensure shared directories exist
```bash
mkdir -p docker-tmp shared
```

Make sure `shared/dbus-session.conf` exists (you can copy a standard D-Bus session config or use your own).

---

### 3. Run the simulator
```bash
sudo docker buildx bake
sudo docker compose up
```

> **Note:** Root privileges are required due to D-Bus and SELinux volume mounts.

---

## 🧠 How It Works

### Engine ECU (ecu.py)
- Starts a session D-Bus daemon inside the container
- Publishes the `com.mercedes.engine` service
- Periodically updates engine telemetry values

### Validation Service (validation.py)
- Waits for the shared D-Bus address from `ecu`
- Connects to the ECU's D-Bus service
- Fetches and prints engine telemetry every 0.5 seconds

---

## 📸 Example Output

```bash
Attaching to ecu-1, validation-1
ecu-1         | [ECU] Starting D-Bus session...
ecu-1         | [ECU] D-Bus session launched: unix:path=/tmp/dbus-eXXXXXXXXXXX,guid=fxxxxxxxxxxxxxxxxxxxx
validation-1  | [Validator] Waiting for D-Bus address...
validation-1  | [Validator] Using DBUS_SESSION_BUS_ADDRESS: unix:path=/tmp/dbus-eXXXXXXXXX,guid=xxxxxxxxxxxxxxxxxx
validation-1  | Validation service starting...
validation-1  | Connecting to DBus...
validation-1  | Successfully connected to ECU service!
validation-1  | 
validation-1  | === Decoded Engine Data ===
validation-1  | Parameter           Value     Unit      Status    
validation-1  | --------------------------------------------------
validation-1  | Rpm                 1555      rpm                 
validation-1  | Speed               18        km/h                
validation-1  | Coolant Temp        82        °C                  
validation-1  | Oil Pressure        1.6       bar                 
validation-1  | Throttle Position   7.0       %                   
validation-1  | Fuel Level          45.5      %                   
validation-1  | Battery Voltage     12.5      V
validation-1  | 
validation-1  | ✅ No active DTCs.
...
```

---

## 🧪 Advanced Ideas

- Add signals: broadcast state changes (e.g., RPM spike)
- Add introspection + D-Bus properties
- Add real-time dashboards (Flask + WebSocket or Grafana)
- Simulate additional ECUs (brake, steering, infotainment)
- Use system bus (`--system`) for more realism
- Add a test suite with `pytest` + `dbus-next`

---

## 💡 Why Linux Native?

This project runs perfect on a Fedora Linux environment:
- Reliable Unix socket IPC (`/tmp/dbus.sock`)
- Full D-Bus support (no hacks like WSLg or xvfb)
- Better SELinux control for volume mounts
- Closer to real-world automotive software environments

---

## 👨‍💻 Contributing

Pull requests and ideas are welcome — especially extensions to simulate more ECUs or diagnostic modules!

---

## 📜 License

MIT — do whatever you want with it, just don't blame me if your engine explodes (virtually).

---

## 📧 Contact

Maintained by [@tallguydesi](https://github.com/tallguydesi)
