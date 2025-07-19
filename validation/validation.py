from shared.signal_definitions import SIGNAL_DEFS
from shared.DTC_definitions import DTC_STORE
from dbus_next.aio import MessageBus
import asyncio
import argparse
import json
from datetime import datetime

ECU_TARGETS = [
    ('com.mercedes.engine', '/com/mercedes/engine'),
]

def log(msg, verbose=True):
    if verbose:
        print(f"[{datetime.now().isoformat()}] {msg}")

def decode_can_frame(frame_bytes):
    data = {}
    for signal, meta in SIGNAL_DEFS.items():
        try:
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
        except Exception as e:
            log(f"[⚠️ Decode Error] {signal}: {e}")
    return data

async def connect_to_ecu(bus, verbose):
    for name, path in ECU_TARGETS:
        log(f"Trying ECU: {name} at {path}", verbose)
        for retries in range(10):
            try:
                introspection = await bus.introspect(name, path)
                ecu = bus.get_proxy_object(name, path, introspection)
                ecu_interface = ecu.get_interface(name)
                log(f"✅ Connected to {name}", verbose)
                return ecu_interface, name
            except Exception as e:
                log(f"Retry {retries + 1} for {name} failed: {e}", verbose)
                await asyncio.sleep(1)
    return None, None

async def main(verbose=False):
    log("Validation service starting...\nConnecting to DBus...", verbose)
    try:
        bus = await MessageBus().connect()
    except Exception as e:
        log(f"Failed to connect to DBus: {e}", verbose)
        return

    ecu_interface, ecu_name = await connect_to_ecu(bus, verbose)
    if not ecu_interface:
        raise Exception("Could not connect to any known ECU")

    while True:
        try:
            state = await ecu_interface.call_get_engine_state()
            frame_hex = await ecu_interface.call_get_engine_frame()
            frame_bytes = bytes.fromhex(frame_hex)
            data = decode_can_frame(frame_bytes)

            with open("last_valid_frame.json", "w") as f:
                json.dump(data, f, indent=2)

            print(f"\n=== Engine State: {state} ===")
            print(f"{'Parameter':<20}{'Value':<10}{'Unit':<10}{'Status':<10}")
            print("-" * 50)

            for param, value in data.items():
                unit = SIGNAL_DEFS[param].get('unit', '')
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

            dtcs = await ecu_interface.call_get_active_dtcs()
            if dtcs:
                print("\n❗ ACTIVE DTCs ❗")
                for code in dtcs:
                    desc = DTC_STORE.get(code, {}).get('description', 'Unknown DTC')
                    print(f"{code}: {desc}")
            else:
                print("\n✅ No active DTCs.")

            print("HEALTHCHECK: OK")

            await asyncio.sleep(1)

        except Exception as e:
            log(f"Error during operation: {e}", verbose)
            log("Attempting to reconnect...", verbose)
            ecu_interface, ecu_name = await connect_to_ecu(bus, verbose)
            if not ecu_interface:
                log("All ECUs offline. Retrying in 5s.", verbose)
                await asyncio.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECU Frame Validator")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    try:
        asyncio.run(main(verbose=args.verbose))
    except Exception as e:
        print(f"Validation service failed: {e}")
        raise

