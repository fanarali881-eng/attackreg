#!/bin/bash
export PROXY_USER=fanar
export PROXY_PASS=j7HGTQiRnys66RIM
export PROXY_HOST=proxy.packetstream.io
export PROXY_PORT=31112
export WAVE_SIZE=10
export WAVE_INTERVAL=45
export STAY_TIME=40
export FORCE_MODE=cloudflare
exec python3 /root/visit.py https://aosallameh.com/ 60
