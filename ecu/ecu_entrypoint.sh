#!/bin/bash

echo "[ECU] Starting D-Bus session..."
eval $(dbus-launch --sh-syntax)

echo "[ECU] D-Bus session launched: $DBUS_SESSION_BUS_ADDRESS"
echo $DBUS_SESSION_BUS_ADDRESS > /tmp/dbus.address

exec python3 ecu.py

