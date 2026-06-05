#!/bin/bash
echo "Stopping any existing CoppeliaSim or Python socket holders..."
pkill -9 -f -i coppelia
pkill -9 -f scratch_

# Make sure port 19997 is free
free_port=1
for i in {1..10}; do
    if ! ss -tulpn | grep -q 19997; then
        free_port=0
        break
    fi
    echo "Waiting for port 19997 to be free..."
    sleep 1
done

if [ $free_port -eq 1 ]; then
    echo "Port 19997 is still occupied! Forcing kill of processes using it..."
    fuser -k -n tcp 19997
    sleep 1
fi

echo "Starting CoppeliaSim headless with nohup..."
nohup env DISPLAY=:1 /home/aics/CoppeliaSim_Pro_V4_7_0_rev4_Ubuntu22_04/coppeliaSim.sh -h -f simulation/simulation.ttt < /dev/null > coppelia.log 2>&1 &
disown

echo "Waiting 4 seconds for CoppeliaSim to initialize and bind port..."
sleep 4

echo "Checking listeners on port 19997..."
ss -tanp | grep 19997

echo "CoppeliaSim started successfully!"
