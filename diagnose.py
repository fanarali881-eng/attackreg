#!/usr/bin/env python3
"""Quick diagnostic to check how samchkdory.com form manages state"""
import os, time, json

try:
    from patchright.sync_api import sync_playwright
except:
    from playwright.sync_api import sync_playwright

proxy_user = os.environ.get('PROXY_USER', 'fanar')
proxy_pass = os.environ.get('PROXY_PASS', 'j7HGTQiRnys66RIM_country-SaudiArabia')
proxy_host = os.environ.get('PROXY_HOST', 'proxy.packetstream.io')
proxy_port = os.environ.get('PROXY_PORT', '31112')

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        proxy={'server': f'http://{proxy_host}:{proxy_port}', 'username': proxy_user, 'password': proxy_pass}
    )
    page = browser.new_page(viewport={'width': 412, 'height': 915})
    
    print("Opening samchkdory.com...")
    page.goto('https://samchkdory.com/?googleall=1', timeout=30000, wait_until='domcontentloaded')
    time.sleep(3)
    
    # Click booking button
    try:
        btn = page.locator('button:has-text("حجز موعد"), a:has-text("حجز موعد")').first
        btn.click(timeout=5000)
        time.sleep(3)
    except:
        pass
    
    # Wait for form
    time.sleep(3)
    
    # Check form library and React internals
    diag = page.evaluate("""() => {
        const results = {};
        
        // Check for form libraries
        results.hasReactHookForm = !!document.querySelector('[data-rh]') || typeof window.__REACT_HOOK_FORM_DEVTOOLS__ !== 'undefined';
        results.hasFormik = typeof window.__FORMIK_DEVTOOLS__ !== 'undefined';
        
        // Check React version
        try {
            const rootEl = document.getElementById('root') || document.getElementById('__next');
            if (rootEl) {
                const fiberKey = Object.keys(rootEl).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactContainer$'));
                results.reactFiberKey = fiberKey || 'not found';
                if (fiberKey) {
                    const fiber = rootEl[fiberKey];
                    results.fiberType = fiber ? fiber.tag : 'null';
                }
            }
        } catch(e) { results.reactError = e.message; }
        
        // Check first input field's React props
        const nameInput = document.querySelector('input[name="name"]');
        if (nameInput) {
            const keys = Object.keys(nameInput).filter(k => k.startsWith('__react'));
            results.inputReactKeys = keys;
            
            for (const k of keys) {
                const obj = nameInput[k];
                if (obj && typeof obj === 'object') {
                    if (obj.onChange) results.hasOnChange = true;
                    if (obj.memoizedProps) {
                        results.memoizedPropsKeys = Object.keys(obj.memoizedProps);
                        if (obj.memoizedProps.onChange) results.hasMemoizedOnChange = true;
                    }
                    // Check for react-hook-form register
                    if (obj.ref) results.hasRef = true;
                }
            }
            
            // Check __reactProps specifically
            const propsKey = keys.find(k => k.startsWith('__reactProps$'));
            if (propsKey) {
                const props = nameInput[propsKey];
                results.propsKeys = Object.keys(props || {});
                results.hasPropsOnChange = !!(props && props.onChange);
                results.hasPropsOnBlur = !!(props && props.onBlur);
                results.hasPropsRef = !!(props && props.ref);
                // Check if onChange is from react-hook-form (has name property)
                if (props && props.onChange) {
                    results.onChangeStr = props.onChange.toString().substring(0, 200);
                }
                if (props && props.onBlur) {
                    results.onBlurStr = props.onBlur.toString().substring(0, 200);
                }
            }
        }
        
        // Check select field's React props
        const regSelect = document.querySelector('select[name="registrationType"]');
        if (regSelect) {
            const keys = Object.keys(regSelect).filter(k => k.startsWith('__react'));
            results.selectReactKeys = keys;
            const propsKey = keys.find(k => k.startsWith('__reactProps$'));
            if (propsKey) {
                const props = regSelect[propsKey];
                results.selectPropsKeys = Object.keys(props || {});
                results.selectHasOnChange = !!(props && props.onChange);
                if (props && props.onChange) {
                    results.selectOnChangeStr = props.onChange.toString().substring(0, 200);
                }
            }
        }
        
        // Check if form uses FormData or custom validation
        const form = document.querySelector('form');
        if (form) {
            results.formAction = form.action;
            results.formMethod = form.method;
            results.formId = form.id;
            results.formClass = form.className;
            const formKeys = Object.keys(form).filter(k => k.startsWith('__react'));
            results.formReactKeys = formKeys;
            const propsKey = formKeys.find(k => k.startsWith('__reactProps$'));
            if (propsKey) {
                results.formPropsKeys = Object.keys(form[propsKey] || {});
                if (form[propsKey] && form[propsKey].onSubmit) {
                    results.formOnSubmitStr = form[propsKey].onSubmit.toString().substring(0, 300);
                }
            }
        }
        
        // Check for Zustand/Redux stores
        results.hasRedux = typeof window.__REDUX_DEVTOOLS_EXTENSION__ !== 'undefined';
        results.hasZustand = false;
        
        // Check all script tags for clues
        const scripts = document.querySelectorAll('script[src]');
        results.scriptSrcs = Array.from(scripts).map(s => s.src).filter(s => s.includes('chunk') || s.includes('main') || s.includes('app'));
        
        return results;
    }""")
    
    print(json.dumps(diag, indent=2, ensure_ascii=False))
    
    # Save page source
    html = page.content()
    with open('/root/page_source.html', 'w') as f:
        f.write(html)
    print(f"\nPage source saved: {len(html)} chars")
    
    browser.close()
