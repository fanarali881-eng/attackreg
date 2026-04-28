import { NextResponse } from 'next/server';
import { Client } from 'ssh2';
import https from 'https';
import http from 'http';

const TEST_SERVER = { host: '46.101.52.177', username: 'root' };

function validateApiKey(req) {
  const authHeader = req.headers.get('x-api-key') || '';
  const validKey = process.env.PANEL_API_KEY;
  if (!validKey || authHeader !== validKey) return false;
  return true;
}

async function runSSHCommand(server, command, timeout = 30000) {
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
      done({ status: 'error', output: output.trim() || 'Timeout' });
    }, timeout);

    conn.on('ready', () => {
      conn.exec(command, { pty: false }, (err, stream) => {
        if (err) {
          clearTimeout(timer);
          return done({ status: 'error', output: err.message });
        }
        stream.on('data', (data) => { output += data.toString(); });
        stream.stderr.on('data', (data) => { /* ignore */ });
        stream.on('close', () => {
          clearTimeout(timer);
          done({ status: 'success', output: output.trim() });
        });
      });
    });

    conn.on('error', (err) => {
      clearTimeout(timer);
      done({ status: 'error', output: err.message });
    });

    conn.connect({
      host: server.host,
      port: 22,
      username: server.username,
      password: process.env.VPS_PASSWORD,
      readyTimeout: 8000,
      keepaliveInterval: 5000,
    });
  });
}

// Direct proxy check - uses HTTP GET through proxy (works with Bright Data)
async function checkProxyDirect(proxyHost, proxyPort, proxyUser, proxyPass) {
  return new Promise((resolve) => {
    let resolved = false;
    const done = (result) => { if (!resolved) { resolved = true; resolve(result); } };

    const timer = setTimeout(() => {
      done({ ok: false, error: 'timeout' });
    }, 25000);

    const auth = Buffer.from(`${proxyUser}:${proxyPass}`).toString('base64');

    // Use HTTP GET through proxy (not CONNECT) - compatible with Bright Data
    const options = {
      host: proxyHost,
      port: parseInt(proxyPort),
      path: 'http://ipv4.icanhazip.com/',
      method: 'GET',
      headers: {
        'Host': 'ipv4.icanhazip.com',
        'Proxy-Authorization': `Basic ${auth}`
      },
      timeout: 20000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk.toString(); });
      res.on('end', () => {
        clearTimeout(timer);
        if (res.statusCode === 407) {
          return done({ ok: false, error: 'auth_failed' });
        }
        if (res.statusCode === 402) {
          return done({ ok: false, error: 'no_balance' });
        }
        if (res.statusCode !== 200) {
          return done({ ok: false, error: `proxy_status_${res.statusCode}` });
        }
        try {
          const ip = data.trim().split('\n').pop().trim();
          if (ip && /^\d+\.\d+\.\d+\.\d+$/.test(ip)) {
            // Get geo info
            const geoReq = http.get(`http://ip-api.com/json/${ip}`, { timeout: 10000 }, (geoRes) => {
              let geoData = '';
              geoRes.on('data', (c) => { geoData += c.toString(); });
              geoRes.on('end', () => {
                try {
                  const geo = JSON.parse(geoData);
                  done({ ok: true, ip, country: geo.country || '?', cc: geo.countryCode || '' });
                } catch(e) {
                  done({ ok: true, ip, country: '?', cc: '' });
                }
              });
            });
            geoReq.on('error', () => { done({ ok: true, ip, country: '?', cc: '' }); });
          } else {
            done({ ok: false, error: 'empty_ip' });
          }
        } catch(e) {
          done({ ok: false, error: 'parse_error' });
        }
      });
    });

    req.on('error', (e) => {
      clearTimeout(timer);
      done({ ok: false, error: e.message });
    });

    req.on('timeout', () => {
      req.destroy();
      clearTimeout(timer);
      done({ ok: false, error: 'timeout' });
    });

    req.end();
  });
}

export async function POST(req) {
  if (!validateApiKey(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { host, port, username, password } = await req.json();

    if (!host || !port || !username || !password) {
      return NextResponse.json({ status: 'error', message: 'بيانات ناقصة' });
    }

    const testPassword = password;

    // Try SSH method first, fallback to direct check
    const credsB64 = Buffer.from(JSON.stringify({
      user: username,
      pass: testPassword,
      host: host,
      port: String(port)
    })).toString('base64');

    const cmd = `python3 -c "
import requests, sys, json, base64
creds = json.loads(base64.b64decode('${credsB64}').decode())
try:
    proxy_url = 'http://' + creds['user'] + ':' + creds['pass'] + '@' + creds['host'] + ':' + creds['port']
    proxies = {'http': proxy_url, 'https': proxy_url}
    r = requests.get('http://ipv4.icanhazip.com', proxies=proxies, timeout=20)
    ip = r.text.strip()
    if ip:
        try:
            geo = requests.get('http://ip-api.com/json/' + ip, timeout=10).json()
            print(json.dumps({'ok': True, 'ip': ip, 'country': geo.get('country','?'), 'cc': geo.get('countryCode','')}))
        except:
            print(json.dumps({'ok': True, 'ip': ip, 'country': '?', 'cc': ''}))
    else:
        print(json.dumps({'ok': False, 'error': 'empty_ip'}))
except requests.exceptions.ProxyError as e:
    err = str(e)
    if '407' in err: print(json.dumps({'ok': False, 'error': 'auth_failed'}))
    elif '402' in err: print(json.dumps({'ok': False, 'error': 'no_balance'}))
    else: print(json.dumps({'ok': False, 'error': 'proxy_error'}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)[:200]}))
"`;

    const result = await runSSHCommand(TEST_SERVER, cmd, 15000);

    let jsonData = null;

    if (result.status === 'success') {
      // SSH worked - parse result
      const lines = result.output.split('\n');
      for (const line of lines) {
        try {
          const parsed = JSON.parse(line.trim());
          if (typeof parsed.ok !== 'undefined') { jsonData = parsed; break; }
        } catch(e) {}
      }
    }

    // If SSH failed or didn't return valid data, try direct check
    if (!jsonData) {
      jsonData = await checkProxyDirect(host, port, username, testPassword);
    }

    if (jsonData.ok) {
      const isSaudi = jsonData.cc === 'SA';
      return NextResponse.json({ 
        status: 'active', 
        message: `✅ البروكسي شغال | IP: ${jsonData.ip} | ${jsonData.country}${isSaudi ? ' 🇸🇦' : ' ⚠️'}`,
        ip: jsonData.ip,
        country: jsonData.country,
        isSaudi
      });
    } else {
      const errorMap = {
        'auth_failed': '❌ خطأ بالمصادقة - تأكد من كلمة المرور',
        'no_balance': '⚠️ الرصيد خلص - يجب إضافة رصيد',
        'proxy_error': '❌ فشل الاتصال بالبروكسي',
        'empty_ip': '❌ البروكسي ما رجع IP',
        'timeout': '❌ انتهت المهلة - البروكسي بطيء'
      };
      const msg = errorMap[jsonData.error] || `❌ خطأ: ${jsonData.error}`;
      const status = jsonData.error === 'no_balance' ? 'expired' : 'error';
      return NextResponse.json({ status, message: msg });
    }

  } catch (error) {
    return NextResponse.json({ status: 'error', message: 'خطأ: ' + error.message }, { status: 500 });
  }
}
