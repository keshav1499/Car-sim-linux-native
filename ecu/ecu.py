from shared.signal_definitions import SIGNAL_DEFS
from shared.DTC_definitions import DTC_STORE
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next import Variant
from enum import Enum
import asyncio
import random


class EngineState(Enum):
    OFF = "OFF"
    CRANKING = "CRANKING"
    RUNNING = "RUNNING"
    FAULT = "FAULT"
    SHUTDOWN = "SHUTDOWN"


class EngineInterface(ServiceInterface):
    def __init__(self):
        super().__init__('com.mercedes.engine')
        self.active_dtcs = []
        self.frame_bytes = bytes(8)
        self.engine_state = EngineState.OFF
        self.state_timer = 0

    def check_dtcs(self, data):
        self.active_dtcs.clear()
        for code, info in DTC_STORE.items():
            if info['trigger'](data):
                self.active_dtcs.append(code)

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

    async def update_data(self):
        while True:
            data = {}

            if self.engine_state == EngineState.OFF:
                self.state_timer += 1
                if self.state_timer > 4:
                    self.state_timer = 0
                    self.engine_state = EngineState.CRANKING

            elif self.engine_state == EngineState.CRANKING:
                data['rpm'] = random.randint(200, 500)
                self.state_timer += 1
                if self.state_timer > 4:
                    self.state_timer = 0
                    self.engine_state = EngineState.RUNNING

            elif self.engine_state == EngineState.RUNNING:
                data['rpm'] = random.randint(800, 6500)
                data['speed'] = random.randint(0, 250)
                data['coolant_temp'] = random.randint(70, 110)
                data['oil_pressure'] = round(random.uniform(1.5, 4.5), 1)
                data['throttle_position'] = round(random.uniform(0, 100), 1)
                data['fuel_level'] = round(random.uniform(0, 100), 1)
                data['battery_voltage'] = round(random.uniform(11.5, 14.8), 1)

                self.check_dtcs(data)
                if 'P0217' in self.active_dtcs:
                    self.engine_state = EngineState.FAULT

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

            for key in SIGNAL_DEFS:
                if key not in data:
                    data[key] = 0

            self.check_dtcs(data)
            self.frame_bytes = self.encode_can_frame(data)
            await asyncio.sleep(0.5)

    @method()
    def get_engine_frame(self) -> 's':
        return self.frame_bytes.hex()

    @method()
    def get_active_dtcs(self) -> 'as':
        return self.active_dtcs

    @method()
    def get_engine_state(self) -> 's':
        return self.engine_state.value


async def main():
    print("Connecting to DBus...")

    try:
        bus = await MessageBus().connect()
        await bus.request_name('com.mercedes.engine')
    except Exception as e:
        print(f"Failed to connect to DBus: {e}")
        return

    interface = EngineInterface()
    bus.export('/com/mercedes/engine', interface)

    print("ECU service started successfully!")
    asyncio.create_task(interface.update_data())
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ECU service failed: {e}")
        raise

