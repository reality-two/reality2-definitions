#!/bin/bash

# Wait a bit
sleep 3 

# Go to Reality2 Dir
cd /home/reality2/reality2 || exit

# Run
./run &

# Wait a bit
sleep 10

# Launch Chromium in kiosk mode
chromium-browser --noerrdialogs --disable-infobars --kiosk https://localhost:4005?map


