from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next import Variant
import asyncio
import random
import os
import time

class EngineECUService:
    def __init__(self):
        self.engine_data = {
            'rpm': Variant('i', 0),  # 'i' for int32
            'speed': Variant('i', 0),
            'coolant_temp': Variant('i', 0),
            'oil_pressure': Variant('d', 0.0),  # 'd' for double
            'throttle_position': Variant('d', 0.0)
        }

    async def update_data(self):
        while True:
            self.engine_data = {
                'rpm': Variant('i', random.randint(800, 6500)),
                'speed': Variant('i', random.randint(0, 250)),
                'coolant_temp': Variant('i', random.randint(70, 110)),
                'oil_pressure': Variant('d', round(random.uniform(1.5, 4.5), 1)),
                'throttle_position': Variant('d', round(random.uniform(0, 100), 1))
            }
            await asyncio.sleep(0.5)

class EngineInterface(ServiceInterface):
    def __init__(self, engine_service):
        super().__init__('com.mercedes.engine')
        self.engine_service = engine_service

    @method()
    def get_engine_data(self) -> 'a{sv}':  # Dictionary of string:variant
        return self.engine_service.engine_data

    @method()
    def get_parameter(self, param: 's') -> 'v':  # Takes string, returns variant
        return self.engine_service.engine_data.get(param, Variant('i', 0))

async def main():
    engine_service = EngineECUService()
    
    # Wait for DBus socket to be ready
    while not os.path.exists('/tmp/dbus.sock'):
        print("Waiting for DBus socket...")
        await asyncio.sleep(0.5)
        
    print("Connecting to DBus...")
    bus = await MessageBus().connect()
    await bus.request_name('com.mercedes.engine')
    
    # Create and export the interface
    interface = EngineInterface(engine_service)
    bus.export('/com/mercedes/engine', interface)
    
    print("ECU service started successfully!")
    
    # Start the data update task
    asyncio.create_task(engine_service.update_data())
    
    # Keep the service running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ECU service failed: {e}")
        raise