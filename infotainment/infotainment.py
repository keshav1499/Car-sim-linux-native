from shared.signal_definitions.infotainment_signals import SIGNAL_DEFS
from shared.DTC_definitions.infotainment_dtcs import DTC_STORE
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from enum import Enum
import asyncio
import random

# -------------------- Infotainment State Enumeration --------------------
class InfotainmentState(Enum):
    OFF = "OFF"
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    ERROR = "ERROR"

# -------------------- Main Infotainment Interface --------------------
class InfotainmentInterface(ServiceInterface):
    def __init__(self):
        super().__init__('com.mercedes.infotainment')
        self.active_dtcs = []
        self.frame_bytes = bytes(6)  # 32-bit (4 bytes) is minimum, here enough for all signals (0-31 bits)
        self.state = InfotainmentState.OFF
        self.state_timer = 0
        self.status_data = {
            "bluetooth_status": "OK",
            "speaker_status": "OK",
            "decoder_status": "OK"
        }

    # -------------------- DTC Evaluation --------------------
    def check_dtcs(self, data, status_data):
        self.active_dtcs.clear()
        full_data = {**data, **status_data}  # Merge for triggers using status flags
        for code, info in DTC_STORE.items():
            if info['trigger'](full_data):
                self.active_dtcs.append(code)

    # -------------------- CAN Frame Encoding --------------------
    def encode_can_frame(self, data):
        max_bit = max(meta['start_bit'] + meta['bit_length'] for meta in SIGNAL_DEFS.values())
        frame_len = (max_bit + 7) // 8
        frame = bytearray(frame_len)
        for signal, meta in SIGNAL_DEFS.items():
            value = data.get(signal, 0)
            raw = int((value - meta['offset']) / meta['scale'])
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

    # -------------------- Infotainment Simulation Loop --------------------
    async def update_data(self):
        while True:
            data = {}
            # State machine for infotainment
            if self.state == InfotainmentState.OFF:
                data['volume_level'] = 0
                data['current_track_id'] = 0
                data['bluetooth_connected'] = 0
                self.status_data = {
                    "bluetooth_status": "OK",
                    "speaker_status": "OK",
                    "decoder_status": "OK"
                }
                self.state_timer += 1
                if self.state_timer > 4:
                    self.state_timer = 0
                    self.state = InfotainmentState.IDLE

            elif self.state == InfotainmentState.IDLE:
                data['volume_level'] = 15
                data['current_track_id'] = 0
                data['bluetooth_connected'] = 1
                self.state_timer += 1
                if self.state_timer > 5:
                    self.state_timer = 0
                    self.state = InfotainmentState.PLAYING

            elif self.state == InfotainmentState.PLAYING:
                data['volume_level'] = random.randint(5, 80)
                data['current_track_id'] = random.randint(1, 250)
                data['bluetooth_connected'] = 1  # Connected
                # Randomly create error scenarios for DTC triggers
                roll = random.random()
                # About 1 in 15 loops, trigger a random error state for a few cycles
                if roll < 0.07:
                    self.status_data["bluetooth_status"] = "ERROR"
                else:
                    self.status_data["bluetooth_status"] = "OK"
                if roll < 0.04:
                    self.status_data["speaker_status"] = "FAULT"
                else:
                    self.status_data["speaker_status"] = "OK"
                if roll < 0.02:
                    self.status_data["decoder_status"] = "FAIL"
                else:
                    self.status_data["decoder_status"] = "OK"
                # Faulty state if anything is not OK
                if any(v != "OK" for v in self.status_data.values()):
                    self.state = InfotainmentState.ERROR

            elif self.state == InfotainmentState.ERROR:
                # Enter error state for some cycles and then recover
                data['volume_level'] = 0
                data['current_track_id'] = 0
                data['bluetooth_connected'] = 0
                self.state_timer += 1
                if self.state_timer > 3:
                    self.state_timer = 0
                    self.state = InfotainmentState.IDLE
                    # Reset error states
                    self.status_data = {
                        "bluetooth_status": "OK",
                        "speaker_status": "OK",
                        "decoder_status": "OK"
                    }

            # Fill missing keys with 0
            for key in SIGNAL_DEFS:
                if key not in data:
                    data[key] = 0

            # Evaluate DTCs
            self.check_dtcs(data, self.status_data)
            # Encode CAN frame
            self.frame_bytes = self.encode_can_frame(data)
            await asyncio.sleep(0.5)

    # -------------------- DBus Methods, names compatible with validation --------------------
#validation should get compatible function calls, ensure the below method calls are compatible
    @method()
    def get_engine_state(self) -> 's':
        # "engine_state" method required by validation.py for all ECUs
        return self.state.value

    @method()
    def get_engine_frame(self) -> 's':
        # Return latest CAN frame as hex string
        return self.frame_bytes.hex()

    @method()
    def get_active_dtcs(self) -> 'as':
        # Return current active DTC list
        return self.active_dtcs

# -------------------- Main DBus Setup --------------------
async def main():
    print("[Infotainment ECU] Connecting to DBus...")
    try:
        bus = await MessageBus().connect()
        await bus.request_name('com.mercedes.infotainment')
    except Exception as e:
        print(f"[Infotainment ECU] Failed to connect to DBus: {e}")
        return
    interface = InfotainmentInterface()
    bus.export('/com/mercedes/infotainment', interface)
    print("[Infotainment ECU] Service started successfully!")
    asyncio.create_task(interface.update_data())
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[Infotainment ECU] Service failed: {e}")
        raise
