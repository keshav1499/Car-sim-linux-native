#!/bin/bash
echo "[Validator] Waiting for D-Bus address..."

while [ ! -f /tmp/dbus.address ]; do
  sleep 0.2
done

export DBUS_SESSION_BUS_ADDRESS=$(cat /tmp/dbus.address)
echo "[Validator] Using DBUS_SESSION_BUS_ADDRESS: $DBUS_SESSION_BUS_ADDRESS"

# Run Python in unbuffered mode
exec python3 -u validation.py
