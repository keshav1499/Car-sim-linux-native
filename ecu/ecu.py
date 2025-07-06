#import os
#print("Current contents of /shared:", os.listdir("/shared"))

#import sys
#sys.path.append("/shared")
from shared.signal_definitions import SIGNAL_DEFS
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
import asyncio
import random

class EngineInterface(ServiceInterface):
    def __init__(self):
        super().__init__('com.mercedes.engine')
        self.frame_bytes = bytes(8)

    def encode_can_frame(self, data):
        frame = bytearray(8)
        for signal, meta in SIGNAL_DEFS.items():
            value = data[signal]
            raw = int((value - meta['offset']) / meta['scale'])
            idx = meta['start_bit'] // 8
            if meta['bit_length'] == 8:
                frame[idx] = raw & 0xFF
            elif meta['bit_length'] == 16:
                frame[idx] = raw & 0xFF
                frame[idx + 1] = (raw >> 8) & 0xFF
        return bytes(frame)

    async def update_data(self):
        while True:
            data = {
                'rpm': random.randint(800, 6500),
                'speed': random.randint(0, 250),
                'coolant_temp': random.randint(70, 110),
                'oil_pressure': round(random.uniform(1.5, 4.5), 1),
                'throttle_position': round(random.uniform(0, 100), 1)
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

