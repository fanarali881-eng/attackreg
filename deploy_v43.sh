#!/bin/bash
cd /tmp/attackreg

SERVERS="138.68.141.40 144.126.234.13 46.101.52.177 142.93.41.217 167.99.94.250 165.22.118.138 138.68.177.243 167.172.61.206 46.101.87.130"
PASS='Fadi@Attack2026!SecureKey#X9'

for server in $SERVERS; do
  echo "[$server] Uploading v43..."
  sshpass -p "$PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 smart_bot.py root@$server:/root/smart_bot.py 2>/dev/null
  if [ $? -eq 0 ]; then
    SIZE=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$server "wc -c /root/smart_bot.py | awk '{print \$1}'" 2>/dev/null)
    echo "[$server] ✅ Upload OK ($SIZE bytes)"
  else
    echo "[$server] ❌ Upload FAILED"
  fi
done

echo ""
echo "=== ALL DEPLOYMENTS DONE ==="
