#!/bin/bash

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Spinner animation
spinner="/|\\-"

# Print startup header
echo -e "${CYAN}"
echo "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"
echo "┃        🚗  MERCEDES VALIDATOR LAUNCH       ┃"
echo "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
echo -e "${NC}"

echo -e "${YELLOW}[Validator] Waiting for D-Bus address...${NC}"

# Spinner while waiting
spin_i=0
while [ ! -f /tmp/dbus.address ]; do
  printf "\r${CYAN}⏳ Waiting ${spinner:spin_i++%${#spinner}:1} ${NC}"
  sleep 0.2
done

echo -e "\n${GREEN}✅ D-Bus address found!${NC}"

export DBUS_SESSION_BUS_ADDRESS=$(cat /tmp/dbus.address)
echo -e "${GREEN}[Validator] Using DBUS_SESSION_BUS_ADDRESS:${NC} ${BOLD}$DBUS_SESSION_BUS_ADDRESS${NC}"

# Section separator
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${YELLOW}Starting Validator Service...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Run Python in unbuffered mode
exec python3 -u validation.py

