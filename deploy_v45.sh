#!/bin/bash
PASS='Fadi@Attack2026!SecureKey#X9'
SERVERS="138.68.141.40 144.126.234.13 46.101.52.177 142.93.41.217 167.99.94.250 165.22.118.138 138.68.177.243 167.172.61.206 46.101.87.130"

for SERVER in $SERVERS; do
    echo "Deploying to $SERVER..."
    sshpass -p "$PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 /tmp/attackreg/smart_bot.py root@$SERVER:/root/smart_bot.py && echo "  ✅ $SERVER done" || echo "  ❌ $SERVER failed"
done

echo ""
echo "Verifying file sizes..."
for SERVER in $SERVERS; do
    SIZE=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$SERVER "wc -c /root/smart_bot.py" 2>/dev/null)
    echo "  $SERVER: $SIZE"
done
echo "Deploy complete!"
