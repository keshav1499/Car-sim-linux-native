from shared.signal_definitions import SIGNAL_DEFS
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next import Variant
import asyncio
import random


class EngineInterface(ServiceInterface):
    def __init__(self):
        super().__init__('com.mercedes.engine')
        self.frame_bytes = bytes(8)

    def encode_can_frame(self, data):
        # Calculate required frame size dynamically
        max_bit = max(meta['start_bit'] + meta['bit_length'] for meta in SIGNAL_DEFS.values())
        frame_len = (max_bit + 7) // 8  # Round up to full byte
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
            data = {
                'rpm': random.randint(800, 6500),
                'speed': random.randint(0, 250),
                'coolant_temp': random.randint(70, 110),
                'oil_pressure': round(random.uniform(1.5, 4.5), 1),
                'throttle_position': round(random.uniform(0, 100), 1),
                'fuel_level': round(random.uniform(0, 100), 1),
                'battery_voltage': round(random.uniform(11.5, 14.8), 1)
            }
            self.frame_bytes = self.encode_can_frame(data)
            await asyncio.sleep(0.5)

    @method()
    def get_engine_frame(self) -> 's':
        return self.frame_bytes.hex()


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

