import { NextResponse } from 'next/server';

const GITHUB_REPO = 'fanarali881-eng/attackreg';
const FILE_PATH = 'servers.json';
const GITHUB_API = `https://api.github.com/repos/${GITHUB_REPO}/contents/${FILE_PATH}`;

// GET: Fetch servers.json from GitHub
export async function GET(req) {
  const authHeader = req.headers.get('x-api-key') || '';
  const validKey = process.env.PANEL_API_KEY;
  if (validKey && authHeader !== validKey) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return NextResponse.json({ error: 'GITHUB_TOKEN not configured' }, { status: 500 });
  }

  try {
    const res = await fetch(GITHUB_API, {
      headers: {
        'Authorization': `token ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'attackreg-dashboard'
      },
      cache: 'no-store'
    });

    if (!res.ok) {
      const errText = await res.text();
      return NextResponse.json({ error: 'GitHub fetch failed', details: errText }, { status: res.status });
    }

    const data = await res.json();
    const content = JSON.parse(Buffer.from(data.content, 'base64').toString('utf-8'));
    return NextResponse.json({ ...content, sha: data.sha });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// PUT: Update servers.json on GitHub
export async function PUT(req) {
  const authHeader = req.headers.get('x-api-key') || '';
  const validKey = process.env.PANEL_API_KEY;
  if (validKey && authHeader !== validKey) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return NextResponse.json({ error: 'GITHUB_TOKEN not configured' }, { status: 500 });
  }

  try {
    const body = await req.json();
    const { servers, sha } = body;

    if (!servers || !Array.isArray(servers)) {
      return NextResponse.json({ error: 'Invalid servers array' }, { status: 400 });
    }

    // If no sha provided, fetch current sha first
    let currentSha = sha;
    if (!currentSha) {
      const getRes = await fetch(GITHUB_API, {
        headers: {
          'Authorization': `token ${token}`,
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'attackreg-dashboard'
        }
      });
      if (getRes.ok) {
        const getData = await getRes.json();
        currentSha = getData.sha;
      }
    }

    const newContent = JSON.stringify({
      version: `v${Date.now()}`,
      servers: servers
    }, null, 2) + '\n';

    const updateBody = {
      message: `Update servers list (${servers.length} servers)`,
      content: Buffer.from(newContent).toString('base64'),
      sha: currentSha
    };

    const updateRes = await fetch(GITHUB_API, {
      method: 'PUT',
      headers: {
        'Authorization': `token ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'attackreg-dashboard',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateBody)
    });

    if (!updateRes.ok) {
      const errText = await updateRes.text();
      return NextResponse.json({ error: 'GitHub update failed', details: errText }, { status: updateRes.status });
    }

    const result = await updateRes.json();
    return NextResponse.json({ success: true, sha: result.content.sha, count: servers.length });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
