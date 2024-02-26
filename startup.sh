#!/bin/bash

export DISPLAY=:0

source /home/sdp/sdpenv/bin/activate
sudo chmod 777 /tmp

python3 /home/sdp/SDP-Camera/main_live_view.py > /home/sdp/app.log 2>&1
