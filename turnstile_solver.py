#!/usr/bin/env python3
"""
Turnstile Solver - Solves Cloudflare Turnstile CAPTCHA using Patchright
Works by creating a local page with the Turnstile widget and solving it automatically.
Used by both visit.py and smart_bot.py to bypass Cloudflare phishing warnings.
"""
import os
import re
import time
import subprocess

# Ensure Xvfb is running for headed mode (Turnstile needs it)
def ensure_display():
    """Start Xvfb if no display is available."""
    if os.environ.get('DISPLAY'):
        return
    try:
        # Check if Xvfb is already running
        result = subprocess.run(['pgrep', '-f', 'Xvfb :99'], capture_output=True)
        if result.returncode != 0:
            subprocess.Popen(
                ['Xvfb', ':99', '-screen', '0', '1920x1080x24', '-nolisten', 'tcp'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(1)
        os.environ['DISPLAY'] = ':99'
    except:
        os.environ['DISPLAY'] = ':99'


def solve_turnstile(site_url, sitekey, timeout=30):
    """
    Solve Cloudflare Turnstile CAPTCHA and return the token.
    Uses Patchright to render a local page with the Turnstile widget.
    
    Args:
        site_url: The URL where Turnstile is embedded (e.g., https://example.com/)
        sitekey: The Turnstile sitekey (e.g., 0x4AAAAAABDaGKKSGLylJZFA)
        timeout: Max seconds to wait for solution (default 30)
    
    Returns:
        str: The Turnstile token, or None if failed
    """
    ensure_display()
    
    try:
        from patchright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠️ Patchright not installed, cannot solve Turnstile", flush=True)
        return None
    
    # HTML template with Turnstile widget
    url_with_slash = site_url if site_url.endswith('/') else site_url + '/'
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Solver</title>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async></script>
    </head>
    <body>
        <div class="cf-turnstile" style="width:70px" data-sitekey="{sitekey}"></div>
    </body>
    </html>
    """
    
    token = None
    start = time.time()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            
            context = browser.new_context(viewport={'width': 800, 'height': 600})
            page = context.new_page()
            
            # Route the site URL to our local HTML
            page.route(url_with_slash, lambda route: route.fulfill(body=html_template, status=200))
            page.goto(url_with_slash, timeout=30000)
            
            time.sleep(2)
            
            # Try to click the widget and wait for token
            for attempt in range(timeout // 2):
                try:
                    val = page.input_value("[name=cf-turnstile-response]", timeout=2000)
                    if val:
                        token = val
                        elapsed = round(time.time() - start, 1)
                        print(f"  ✅ Turnstile solved in {elapsed}s", flush=True)
                        break
                    else:
                        if attempt < 5:
                            try:
                                page.locator("//div[@class='cf-turnstile']").click(timeout=1000)
                            except:
                                pass
                        time.sleep(1)
                except:
                    time.sleep(1)
            
            browser.close()
    except Exception as e:
        print(f"  ⚠️ Turnstile solver error: {e}", flush=True)
    
    return token


def bypass_cloudflare_phishing(site_url, proxy_url=None, timeout=30):
    """
    Full bypass of Cloudflare phishing warning page.
    
    1. Fetches the phishing page to get atok and sitekey
    2. Solves Turnstile CAPTCHA
    3. Submits the bypass form
    4. Returns cookies that allow access to the site
    
    Args:
        site_url: The URL with phishing warning (e.g., https://example.com/)
        proxy_url: HTTP proxy URL (e.g., http://user:pass@host:port)
        timeout: Max seconds for Turnstile solving
    
    Returns:
        dict: {"cookies": {...}, "success": True} or {"cookies": {}, "success": False}
    """
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        print("  ⚠️ curl_cffi not installed", flush=True)
        return {"cookies": {}, "success": False}
    
    proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    # Step 1: Get the phishing page
    print("  📄 Fetching phishing page...", flush=True)
    try:
        r = cffi_requests.get(site_url, impersonate='chrome131', headers=headers,
                              proxies=proxies, timeout=20, verify=False)
    except Exception as e:
        print(f"  ⚠️ Failed to fetch page: {e}", flush=True)
        return {"cookies": {}, "success": False}
    
    # Check if it's actually a phishing page
    if r.status_code == 200 and 'phishing' not in r.text.lower():
        print("  ✅ No phishing page - site is accessible!", flush=True)
        return {"cookies": dict(r.cookies), "success": True, "html": r.text}
    
    # Extract atok
    atok_match = re.search(r'name="atok"\s+value="([^"]+)"', r.text)
    if not atok_match:
        print("  ⚠️ No atok found in phishing page", flush=True)
        return {"cookies": {}, "success": False}
    atok = atok_match.group(1)
    
    # Extract sitekey
    sitekey_match = re.search(r'data-sitekey=["\']([^"\']+)["\']', r.text)
    if not sitekey_match:
        print("  ⚠️ No sitekey found in phishing page", flush=True)
        return {"cookies": {}, "success": False}
    sitekey = sitekey_match.group(1)
    
    print(f"  🔑 atok: {atok[:30]}... | sitekey: {sitekey}", flush=True)
    
    # Step 2: Solve Turnstile
    print("  🧩 Solving Turnstile CAPTCHA...", flush=True)
    token = solve_turnstile(site_url, sitekey, timeout=timeout)
    
    if not token:
        print("  ❌ Failed to solve Turnstile", flush=True)
        return {"cookies": {}, "success": False}
    
    # Step 3: Submit bypass form (GET method)
    print("  📤 Submitting bypass form...", flush=True)
    bypass_url = site_url.rstrip('/') + '/cdn-cgi/phish-bypass'
    params = {
        'atok': atok,
        'original_path': '/',
        'cf-turnstile-response': token
    }
    
    try:
        session = cffi_requests.Session(impersonate='chrome131')
        r2 = session.get(bypass_url, params=params, headers={**headers, 'Referer': site_url},
                         proxies=proxies, timeout=20, verify=False, allow_redirects=True)
        
        cookies = dict(session.cookies)
        
        if r2.status_code == 200 and 'phishing' not in r2.text.lower():
            print(f"  ✅ Phishing bypass successful! Cookie: __cf_mw_byp", flush=True)
            return {"cookies": cookies, "success": True, "html": r2.text}
        else:
            print(f"  ⚠️ Bypass returned status {r2.status_code}", flush=True)
            return {"cookies": cookies, "success": False}
    except Exception as e:
        print(f"  ⚠️ Bypass submission error: {e}", flush=True)
        return {"cookies": {}, "success": False}


if __name__ == "__main__":
    # Test
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://sesallameh.com/"
    proxy = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = bypass_cloudflare_phishing(url, proxy_url=proxy)
    print(f"\nResult: {result}")
