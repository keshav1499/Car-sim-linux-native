from shared.signal_definitions import SIGNAL_DEFS  # CAN signal definitions (start_bit, bit_length, scale, offset)
from shared.DTC_definitions import DTC_STORE       # Diagnostic Trouble Code definitions and triggers
from dbus_next.aio import MessageBus               # Async DBus message bus
from dbus_next.service import ServiceInterface, method  # DBus interface and method decorator
from dbus_next import Variant
from enum import Enum
import asyncio
import random


# -------------------- Engine State Enumeration --------------------
# Represents the state machine for engine simulation.
class EngineState(Enum):
    OFF = "OFF"
    CRANKING = "CRANKING"
    RUNNING = "RUNNING"
    FAULT = "FAULT"
    SHUTDOWN = "SHUTDOWN"


# -------------------- Main Engine Interface Class --------------------
# Implements the DBus service that simulates an ECU interface.
class EngineInterface(ServiceInterface):
    def __init__(self):
        super().__init__('com.mercedes.engine')  # DBus interface name
        self.active_dtcs = []                   # List of currently active DTC codes
        self.frame_bytes = bytes(8)             # Placeholder for the encoded CAN frame
        self.engine_state = EngineState.OFF     # Initial engine state
        self.state_timer = 0                    # Internal timer to control state transitions

    # -------------------- DTC Evaluation --------------------
    # Clears and re-evaluates DTCs based on current sensor data.
    def check_dtcs(self, data):
        self.active_dtcs.clear()
        for code, info in DTC_STORE.items():
            if info['trigger'](data):          # Each DTC has a 'trigger' function
                self.active_dtcs.append(code)

    # -------------------- CAN Frame Encoding --------------------
    # Encodes current sensor data into an 8-byte CAN frame.
    def encode_can_frame(self, data):
        max_bit = max(meta['start_bit'] + meta['bit_length'] for meta in SIGNAL_DEFS.values())
        frame_len = (max_bit + 7) // 8
        frame = bytearray(frame_len)

        for signal, meta in SIGNAL_DEFS.items():
            value = data.get(signal, 0)
            raw = int((value - meta['offset']) / meta['scale'])  # Convert value to raw using offset/scale
            idx = meta['start_bit'] // 8
            bit_len = meta['bit_length']

            if bit_len == 8:
                frame[idx] = raw & 0xFF
            elif bit_len == 16:
                frame[idx] = raw & 0xFF
                frame[idx + 1] = (raw >> 8) & 0xFF
            else:
                raise NotImplementedError(f"Unsupported bit length: {bit_len} for signal {signal}")

        return bytes(frame)

    # -------------------- ECU Simulation Loop --------------------
    # Runs continuously and updates engine state and sensor values.
    async def update_data(self):
        while True:
            data = {}

            # State: Engine is off
            if self.engine_state == EngineState.OFF:
                self.state_timer += 1
                if self.state_timer > 4:
                    self.state_timer = 0
                    self.engine_state = EngineState.CRANKING

            # State: Cranking - low rpm, preparing to start
            elif self.engine_state == EngineState.CRANKING:
                data['rpm'] = random.randint(200, 500)
                self.state_timer += 1
                if self.state_timer > 4:
                    self.state_timer = 0
                    self.engine_state = EngineState.RUNNING

            # State: Running - normal engine operation
            elif self.engine_state == EngineState.RUNNING:
                data['rpm'] = random.randint(800, 6500)
                data['speed'] = random.randint(0, 250)
                data['coolant_temp'] = random.randint(70, 110)
                data['oil_pressure'] = round(random.uniform(1.5, 4.5), 1)
                data['throttle_position'] = round(random.uniform(0, 100), 1)
                data['fuel_level'] = round(random.uniform(0, 100), 1)
                data['battery_voltage'] = round(random.uniform(11.5, 14.8), 1)

                self.check_dtcs(data)
                if 'P0217' in self.active_dtcs:  # Overheat condition
                    self.engine_state = EngineState.FAULT

            # State: Fault - engine failure mode, enters shutdown soon
            elif self.engine_state == EngineState.FAULT:
                data = {
                    'rpm': 0,
                    'speed': 0,
                    'coolant_temp': 120,
                    'oil_pressure': 0.0,
                    'throttle_position': 0,
                    'fuel_level': 50,
                    'battery_voltage': 11.5
                }
                self.state_timer += 1
                if self.state_timer > 6:
                    self.state_timer = 0
                    self.engine_state = EngineState.SHUTDOWN

            # State: Shutdown - engine cooling down before turning off
            elif self.engine_state == EngineState.SHUTDOWN:
                data = {
                    'rpm': 0,
                    'speed': 0,
                    'coolant_temp': 60,
                    'oil_pressure': 0.0,
                    'throttle_position': 0,
                    'fuel_level': 50,
                    'battery_voltage': 11.5
                }
                self.state_timer += 1
                if self.state_timer > 5:
                    self.state_timer = 0
                    self.engine_state = EngineState.OFF

            # Fill missing keys with default 0 if not set above
            for key in SIGNAL_DEFS:
                if key not in data:
                    data[key] = 0

            self.check_dtcs(data)                          # Evaluate DTCs
            self.frame_bytes = self.encode_can_frame(data)  # Encode the new frame

            await asyncio.sleep(0.5)  # Delay for next update (simulate 2 Hz refresh rate)

    # -------------------- DBus Method: Get CAN Frame --------------------
    # Returns the latest CAN frame as a hex string
    @method()
    def get_engine_frame(self) -> 's':
        return self.frame_bytes.hex()

    # -------------------- DBus Method: Get Active DTCs --------------------
    # Returns list of current Diagnostic Trouble Codes
    @method()
    def get_active_dtcs(self) -> 'as':
        return self.active_dtcs

    # -------------------- DBus Method: Get Engine State --------------------
    # Returns current engine state as a string
    @method()
    def get_engine_state(self) -> 's':
        return self.engine_state.value


# -------------------- Main DBus Setup --------------------
# Connects to DBus, registers the engine interface, and starts the simulation loop.
async def main():
    print("Connecting to DBus...")

    try:
        bus = await MessageBus().connect()
        await bus.request_name('com.mercedes.engine')  # Claim DBus name
    except Exception as e:
        print(f"Failed to connect to DBus: {e}")
        return

    interface = EngineInterface()
    bus.export('/com/mercedes/engine', interface)  # Expose object path

    print("ECU service started successfully!")
    asyncio.create_task(interface.update_data())   # Start simulation in background
    await asyncio.Event().wait()                   # Keep service running


# -------------------- Entry Point --------------------
# Starts the event loop if executed directly
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ECU service failed: {e}")
        raise