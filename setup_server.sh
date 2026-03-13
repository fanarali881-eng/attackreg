#!/bin/bash
set -e
echo "=== Installing Docker ==="
if ! which docker > /dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
echo "=== Installing Python deps ==="
pip3 install --break-system-packages curl_cffi requests -q 2>/dev/null || pip3 install curl_cffi requests -q 2>/dev/null || true
echo "=== Pulling FlareSolverr ==="
docker pull ghcr.io/flaresolverr/flaresolverr:latest 2>/dev/null || true
echo "=== Starting 10 FlareSolverr instances with 768MB ==="
for i in $(seq 1 10); do
    port=$((8190 + i))
    name="flaresolverr${i}"
    docker rm -f $name 2>/dev/null || true
    docker run -d --name $name --restart=unless-stopped -p ${port}:8191 \
        -e LOG_LEVEL=info \
        --memory=768m \
        --shm-size=256m \
        ghcr.io/flaresolverr/flaresolverr:latest
    echo "  Started $name on port $port"
done
echo "=== Waiting for startup ==="
sleep 15
ok=0
for port in $(seq 8191 8200); do
    if curl -s http://localhost:$port/ 2>/dev/null | grep -q "FlareSolverr"; then ok=$((ok+1)); fi
done
echo "  $ok/10 instances ready!"
echo "=== SETUP DONE ==="
