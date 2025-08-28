#!/bin/bash

# Colors (same as before)
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

spinner="/|\\-"

echo -e "${CYAN}"
echo "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"
echo "┃        🚗  MERCEDES VALIDATOR LAUNCH       ┃"
echo "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
echo -e "${NC}"

echo -e "${YELLOW}[Validator] Waiting for /tmp/dbus.engine.address...${NC}"
spin_i=0
while [ ! -f /tmp/dbus.engine.address ]; do
  printf "\r${CYAN}⏳ Waiting ${spinner:spin_i++%${#spinner}:1} ${NC}"
  sleep 0.2
done

echo -e "\n${GREEN}✅ Found /tmp/dbus.engine.address${NC}"

echo -e "${YELLOW}[Validator] Waiting for /tmp/dbus.infotainment.address...${NC}"
spin_i=0
while [ ! -f /tmp/dbus.infotainment.address ]; do
  printf "\r${CYAN}⏳ Waiting ${spinner:spin_i++%${#spinner}:1} ${NC}"
  sleep 0.2
done

echo -e "\n${GREEN}✅ Found /tmp/dbus.infotainment.address${NC}"

# Read addresses from file
ENGINE_DBUS_ADDR=$(cat /tmp/dbus.engine.address)
INFOTAINMENT_DBUS_ADDR=$(cat /tmp/dbus.infotainment.address)

echo -e "${GREEN}[Validator] Using D-Bus addresses:${NC}"
echo -e "Engine:      ${ENGINE_DBUS_ADDR}"
echo -e "Infotainment: ${INFOTAINMENT_DBUS_ADDR}"

# Export both addresses as environment variables for the Python script
export DBUS_ENGINE_ADDRESS="$ENGINE_DBUS_ADDR"
export DBUS_INFOTAINMENT_ADDRESS="$INFOTAINMENT_DBUS_ADDR"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${YELLOW}Starting Validator Service...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Run Python in unbuffered mode
exec python3 -u validation.py #--verbose
