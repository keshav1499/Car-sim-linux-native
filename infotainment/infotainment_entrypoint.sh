#!/bin/bash
echo "[Infotainment] Starting D-Bus session..."
eval $(dbus-launch --sh-syntax)
echo "[Infotainment] D-Bus session launched: $DBUS_SESSION_BUS_ADDRESS"
echo $DBUS_SESSION_BUS_ADDRESS > /tmp/dbus.infotainment.address
exec python3 infotainment.py
