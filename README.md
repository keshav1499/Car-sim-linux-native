
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
├── docker-bake.hcl
├── docker-compose.yml
├── docker-tmp
│   ├── dbus.engine.address
│   ├── dbus.infotainment.address
├── ecu
│   ├── Dockerfile
│   ├── ecu_entrypoint.sh
│   ├── ecu.py
│   └── requirements.txt
├── infotainment
│   ├── Dockerfile
│   ├── infotainment_entrypoint.sh
│   ├── infotainment.py
│   └── requirements.txt
├── LICENSE
├── README.md
├── shared
│   ├── dbus-session.conf
│   ├── DTC_definitions
│   │   ├── engine_dtcs.py
│   │   ├── infotainment_dtcs.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── __pycache__
│   │   └── signal_definitions.cpython-39.pyc
│   └── signal_definitions
│       ├── engine_signals.py
│       ├── infotainment_signals.py
│       └── __init__.py
└── validation
    ├── Dockerfile
    ├── requirements.txt
    ├── validation.py
    ├── validation.py.save
    └── validator_entrypoint.sh
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
docker compose up  
[+] Running 3/3
 ✔ Container car-sim-linux-native-infotainment-1  Created                                0.1s 
 ✔ Container car-sim-linux-native-ecu-1           Recreated                              0.1s 
 ✔ Container car-sim-linux-native-validation-1    Recreated                              0.1s 
Attaching to ecu-1, infotainment-1, validation-1
ecu-1  | [ECU] Starting D-Bus session...
ecu-1  | [ECU] D-Bus session launched: unix:path=/tmp/dbus-rbHWwiS0fC,guid=eca5e701607c987b58bedec468afee8a
infotainment-1  | [Infotainment] Starting D-Bus session...
infotainment-1  | [Infotainment] D-Bus session launched: unix:path=/tmp/dbus-H7ilt5JzzQ,guid=6b848215eefd97fdeb85780968afee8a
validation-1    | 
validation-1    | ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
validation-1    | ┃        🚗  MERCEDES VALIDATOR LAUNCH       ┃
validation-1    | ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
validation-1    | 
validation-1    | [Validator] Waiting for /tmp/dbus.engine.address...
validation-1    | 
validation-1    | ✅ Found /tmp/dbus.engine.address
validation-1    | [Validator] Waiting for /tmp/dbus.infotainment.address...
validation-1    | 
validation-1    | ✅ Found /tmp/dbus.infotainment.address
validation-1    | [Validator] Using D-Bus addresses:
validation-1    | Engine:      unix:path=/tmp/dbus-rbHWwiS0fC,guid=eca5e701607c987b58bedec468afee8a
validation-1    | Infotainment: unix:path=/tmp/dbus-H7ilt5JzzQ,guid=6b848215eefd97fdeb85780968afee8a
validation-1    | ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
validation-1    | Starting Validator Service...
validation-1    | ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
validation-1    | 
validation-1    | === [com.mercedes.engine] State: OFF ===
validation-1    | Parameter           Value     Unit      Status    
validation-1    | --------------------------------------------------
validation-1    | Rpm                 0         rpm                 
validation-1    | Speed               0         km/h                
validation-1    | Coolant Temp        0         °C                  
validation-1    | Oil Pressure        0.0       bar       ⚠️        
validation-1    | Throttle Position   0.0       %                   
validation-1    | Fuel Level          0.0       %         ⚠️        
validation-1    | Battery Voltage     0.0       V         ⚠️        
validation-1    | 
validation-1    | === [com.mercedes.infotainment] State: OFF ===
validation-1    | Parameter           Value     Unit      Status    
validation-1    | --------------------------------------------------
validation-1    | Volume Level        0         %                   
validation-1    | Current Track Id    0         id                  
validation-1    | Bluetooth Connected 0         bool                
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

Maintained by [@tallguydesi](https://github.com/keshav1499)
