#!/bin/bash
eval `dbus-launch --sh-syntax`
echo $DBUS_SESSION_BUS_ADDRESS > /tmp/dbus-address
python3 ecu_service.py
