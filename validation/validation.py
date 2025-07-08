from shared.signal_definitions import SIGNAL_DEFS
from shared.DTC_definitions import DTC_STORE
from dbus_next.aio import MessageBus
import asyncio

def decode_can_frame(frame_bytes):
    data = {}

    for signal, meta in SIGNAL_DEFS.items():
        idx = meta['start_bit'] // 8
        bit_len = meta['bit_length']

        if bit_len == 8:
            raw = frame_bytes[idx]
        elif bit_len == 16:
            raw = frame_bytes[idx] | (frame_bytes[idx + 1] << 8)
        else:
            raise NotImplementedError(f"Unsupported bit length: {bit_len} for signal {signal}")

        value = raw * meta['scale'] + meta['offset']
        data[signal] = round(value, 1)

    return data

async def main():
    print("Validation service starting...\nConnecting to DBus...")
    try:
        bus = await MessageBus().connect()
    except Exception as e:
        print(f"Failed to connect to DBus: {e}")
        return

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

    while True:
        try:
            frame_hex = await ecu_interface.call_get_engine_frame()
            frame_bytes = bytes.fromhex(frame_hex)
            data = decode_can_frame(frame_bytes)

            print("\n=== Decoded Engine Data ===")
            print(f"{'Parameter':<20}{'Value':<10}{'Unit':<10}{'Status':<10}")
            print("-" * 50)

            for param, value in data.items():
                unit = SIGNAL_DEFS[param]['unit']
                status = ''
                if param == 'rpm' and value > 6000:
                    status = '⚠️'
                if param == 'coolant_temp' and value > 105:
                    status = '⚠️'
                if param == 'oil_pressure' and (value < 1.5 or value > 4.5):
                    status = '⚠️'
                if param == 'throttle_position' and value > 90:
                    status = '⚠️'
                if param == 'fuel_level' and value < 10:
                    status = '⚠️'
                if param == 'battery_voltage' and value < 12:
                    status = '⚠️'
                print(f"{param.replace('_', ' ').title():<20}{value:<10}{unit:<10}{status:<10}")

            # Fetch and print active DTCs
            dtcs = await ecu_interface.call_get_active_dtcs()
            if dtcs:
                print("\n❗ ACTIVE DTCs ❗")
                for code in dtcs:
                    desc = DTC_STORE.get(code, {}).get('description', 'Unknown DTC')
                    print(f"{code}: {desc}")
            else:
                print("\n✅ No active DTCs.")

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

