#!/bin/bash
export DISPLAY=:99
# Start Xvfb if not running
pgrep -f 'Xvfb :99' > /dev/null || (Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &)
sleep 1

# Set proxy
export PROXY_USER='fanar'
export PROXY_PASS='j7HGTQiRnys66RIM_country-SaudiArabia'
export PROXY_HOST='proxy.packetstream.io'
export PROXY_PORT='31112'

# Clear old log
> /root/smart_bot.log

# Run bot: 1 instance, 5 min duration, targeting samchkdory.com
echo "Starting bot v43 test on samchkdory.com..."
python3 /root/smart_bot.py 'https://samchkdory.com' 5 1 >> /root/smart_bot.log 2>&1 &
BOT_PID=$!
echo "Bot PID: $BOT_PID"
echo $BOT_PID > /root/bot_pid.txt
