from dbus_next.aio import MessageBus
import asyncio

async def main():
    print("Validation service starting...")

    print("Connecting to DBus...")
    try:
        bus = await MessageBus().connect()
    except Exception as e:
        print(f"Failed to connect to DBus: {e}")
        return

    # Try to connect to ECU service
    retries = 0
    ecu_interface = None
    while retries < 10:
        try:
            introspection = await bus.introspect('com.mercedes.engine', '/com/mercedes/engine')
            ecu = bus.get_proxy_object('com.mercedes.engine', '/com/mercedes/engine', introspection)
            ecu_interface = ecu.get_interface('com.mercedes.engine')
            print("Successfully connected to ECU service!")
            break
        except Exception as e:
            print(f"Connection attempt {retries + 1} failed: {e}")
            retries += 1
            await asyncio.sleep(1)

    if not ecu_interface:
        raise Exception("Could not connect to ECU service after 10 attempts")

    print("Validation service running. Monitoring engine data...")

    while True:
        try:
            data = await ecu_interface.call_get_engine_data()

            # Extract values from Variants
            rpm = data['rpm'].value
            speed = data['speed'].value
            coolant_temp = data['coolant_temp'].value
            oil_pressure = data['oil_pressure'].value
            throttle_position = data['throttle_position'].value

            print("\n=== Engine Data ===")
            print(f"{'Parameter':<20}{'Value':<10}{'Unit':<10}{'Status':<10}")
            print("-" * 50)
            print(f"{'RPM':<20}{rpm:<10}{'rpm':<10}{'⚠️' if rpm > 6000 and speed < 50 else ''}")
            print(f"{'Speed':<20}{speed:<10}{'km/h':<10}")
            print(f"{'Coolant Temp':<20}{coolant_temp:<10}{'°C':<10}{'⚠️' if coolant_temp > 105 else ''}")
            print(f"{'Oil Pressure':<20}{oil_pressure:<10.1f}{'bar':<10}{'⚠️' if oil_pressure < 1.5 or oil_pressure > 4.5 else ''}")
            print(f"{'Throttle Pos':<20}{throttle_position:<10.1f}{'%':<10}{'⚠️' if throttle_position > 90 else ''}")

            if rpm > 6000 and speed < 50:
                print("WARNING: High RPM at low speed!")
            if coolant_temp > 105:
                print("WARNING: Coolant temperature too high!")
            if oil_pressure < 1.5:
                print("WARNING: Oil pressure too low!")
            if oil_pressure > 4.5:
                print("WARNING: Oil pressure too high!")
            if throttle_position > 90:
                print("WARNING: High throttle position!")

            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error during operation: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Validation service failed: {e}")
        raise

