import os
import importlib
import asyncio
import argparse
import json
from dbus_next.aio import MessageBus
from datetime import datetime


ECU_TARGETS = [
    {
        "name": "com.mercedes.engine",
        "path": "/com/mercedes/engine",
        "signals": "engine_signals",
        "dtcs": "engine_dtcs",
        "dbus_env_var": "DBUS_ENGINE_ADDRESS",
    },
    {
        "name": "com.mercedes.infotainment",
        "path": "/com/mercedes/infotainment",
        "signals": "infotainment_signals",
        "dtcs": "infotainment_dtcs",
        "dbus_env_var": "DBUS_INFOTAINMENT_ADDRESS",
    }
]


def log(msg, verbose=True):
    if verbose:
        print(f"[{datetime.now().isoformat()}] {msg}")


def load_ecu_definitions(signals_module_name, dtc_module_name):
    """Dynamically import signal definitions and DTCs for the specific ECU."""
    signals_mod = importlib.import_module(f"shared.signal_definitions.{signals_module_name}")
    dtcs_mod = importlib.import_module(f"shared.DTC_definitions.{dtc_module_name}")
    return signals_mod.SIGNAL_DEFS, dtcs_mod.DTC_STORE


def decode_can_frame(frame_bytes, signal_defs):
    """Decode CAN frame to signal values based on given signal defs."""
    data = {}
    for signal, meta in signal_defs.items():
        try:
            idx = meta['start_bit'] // 8
            bit_len = meta['bit_length']
            # Only support 8 or 16 bit signals
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


async def connect_to_ecu(bus, ecu, verbose):
    """Try connecting to a given ECU on DBus, with retries."""
    name = ecu["name"]
    path = ecu["path"]
    for retries in range(10):
        try:
            introspection = await bus.introspect(name, path)
            proxy = bus.get_proxy_object(name, path, introspection)
            ecu_interface = proxy.get_interface(name)
            log(f"✅ Connected to {name}", verbose)
            return ecu_interface
        except Exception as e:
            log(f"Retry {retries + 1} for {name} failed: {e}", verbose)
            await asyncio.sleep(1)
    log(f"❌ Could not connect to {name}", verbose)
    return None


async def poll_ecu(bus, ecu, verbose):
    """Polling loop for a single ECU (connect, decode, display in loop)."""
    SIGNAL_DEFS, DTC_STORE = load_ecu_definitions(ecu["signals"], ecu["dtcs"])
    ecu_name = ecu["name"]
    ecu_interface = await connect_to_ecu(bus, ecu, verbose)
    if not ecu_interface:
        log(f"Could not connect to {ecu_name}", verbose)
        return

    json_filename = f"last_valid_frame_{ecu_name.replace('.', '_')}.json"

    while True:
        try:
            # These method names should match the interface definition for each ECU
            state = await ecu_interface.call_get_engine_state()
            frame_hex = await ecu_interface.call_get_engine_frame()
            frame_bytes = bytes.fromhex(frame_hex)
            data = decode_can_frame(frame_bytes, SIGNAL_DEFS)
            with open(json_filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"\n=== [{ecu_name}] State: {state} ===")
            print(f"{'Parameter':<20}{'Value':<10}{'Unit':<10}{'Status':<10}")
            print("-" * 50)
            for param, value in data.items():
                unit = SIGNAL_DEFS[param].get('unit', '')
                status = ''
                # Highlight "warn" conditions for standard auto parameters, else skip status
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
            # DTCs (if any)
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
            log(f"[{ecu_name}] Error during operation: {e}", verbose)
            log(f"[{ecu_name}] Attempting to reconnect...", verbose)
            ecu_interface = await connect_to_ecu(bus, ecu, verbose)
            if not ecu_interface:
                log(f"[{ecu_name}] ECU offline. Retrying in 5s.", verbose)
                await asyncio.sleep(5)


async def main(verbose=False):
    log("Validation service starting...\nConnecting to DBus sessions...", verbose)

    tasks = []
    for ecu in ECU_TARGETS:
        dbus_address = os.getenv(ecu["dbus_env_var"])
        if not dbus_address:
            log(f"Missing environment variable {ecu['dbus_env_var']} for {ecu['name']}, skipping.", verbose)
            continue
        try:
            log(f"Setting DBUS_SESSION_BUS_ADDRESS for {ecu['name']}", verbose)
            os.environ['DBUS_SESSION_BUS_ADDRESS'] = dbus_address
            bus = await MessageBus().connect()
            log(f"Connected to {ecu['name']} DBus", verbose)
        except Exception as e:
            log(f"Failed to connect to D-Bus at {dbus_address} for {ecu['name']}: {e}", verbose)
            continue
        tasks.append(asyncio.create_task(poll_ecu(bus, ecu, verbose)))

    if not tasks:
        log("No ECU connections established, exiting.", verbose)
        return

    log(f"Starting polling for {len(tasks)} ECUs", verbose)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECU Frame Validator")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    try:
        asyncio.run(main(verbose=args.verbose))
    except Exception as e:
        print(f"Validation service failed: {e}")
        raise