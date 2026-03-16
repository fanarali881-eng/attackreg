#!/usr/bin/env python3
"""Diagnostic v2 - wait for form, check React internals"""
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
    time.sleep(5)
    
    # Check if homepage loaded
    text = page.evaluate("document.body.innerText.substring(0, 200)")
    print(f"Page text: {text[:100]}")
    
    # Click booking button
    try:
        btns = page.locator('button:has-text("حجز موعد"), a:has-text("حجز موعد")')
        count = btns.count()
        print(f"Found {count} booking buttons")
        if count > 0:
            btns.first.click(timeout=5000)
            print("Clicked booking button")
    except Exception as e:
        print(f"Button click error: {e}")
    
    # Wait for form to load
    time.sleep(5)
    
    # Check for form fields
    input_count = page.evaluate("document.querySelectorAll('input').length")
    select_count = page.evaluate("document.querySelectorAll('select').length")
    print(f"Inputs: {input_count}, Selects: {select_count}")
    
    if input_count == 0:
        # Try clicking again or wait more
        time.sleep(5)
        input_count = page.evaluate("document.querySelectorAll('input').length")
        print(f"After wait - Inputs: {input_count}")
    
    # Now check React props on the name input
    diag = page.evaluate("""() => {
        const results = {};
        
        // Check name input
        const nameInput = document.querySelector('input[name="name"]');
        if (nameInput) {
            results.nameInputFound = true;
            const allKeys = Object.keys(nameInput);
            results.allKeys = allKeys.filter(k => k.startsWith('__'));
            
            const propsKey = allKeys.find(k => k.startsWith('__reactProps$'));
            if (propsKey) {
                const props = nameInput[propsKey];
                results.propsKeys = Object.keys(props || {});
                
                if (props.onChange) {
                    results.onChangeType = typeof props.onChange;
                    results.onChangeStr = props.onChange.toString().substring(0, 300);
                }
                if (props.onBlur) {
                    results.onBlurStr = props.onBlur.toString().substring(0, 200);
                }
                if (props.ref) {
                    results.refType = typeof props.ref;
                    results.refStr = String(props.ref).substring(0, 100);
                }
                results.propsValue = props.value;
                results.propsDefaultValue = props.defaultValue;
            }
            
            const fiberKey = allKeys.find(k => k.startsWith('__reactFiber$'));
            if (fiberKey) {
                const fiber = nameInput[fiberKey];
                results.fiberTag = fiber ? fiber.tag : null;
                results.fiberType = fiber ? String(fiber.type) : null;
                if (fiber && fiber.memoizedProps) {
                    results.memoizedPropsKeys = Object.keys(fiber.memoizedProps);
                    if (fiber.memoizedProps.onChange) {
                        results.memoizedOnChangeStr = fiber.memoizedProps.onChange.toString().substring(0, 300);
                    }
                }
                // Walk up the fiber tree to find the form component
                let parent = fiber;
                const parentTypes = [];
                for (let i = 0; i < 10 && parent; i++) {
                    if (parent.type && typeof parent.type === 'function') {
                        parentTypes.push(parent.type.name || parent.type.displayName || 'anonymous');
                    }
                    parent = parent.return;
                }
                results.parentComponents = parentTypes;
            }
        } else {
            results.nameInputFound = false;
        }
        
        // Check select
        const sel = document.querySelector('select[name="registrationType"]');
        if (sel) {
            const propsKey = Object.keys(sel).find(k => k.startsWith('__reactProps$'));
            if (propsKey) {
                const props = sel[propsKey];
                results.selectPropsKeys = Object.keys(props || {});
                if (props.onChange) {
                    results.selectOnChangeStr = props.onChange.toString().substring(0, 300);
                }
            }
        }
        
        // Type into name field and check if React state updates
        if (nameInput) {
            // First, let's see what happens when we manually call onChange
            const propsKey = Object.keys(nameInput).find(k => k.startsWith('__reactProps$'));
            if (propsKey && nameInput[propsKey] && nameInput[propsKey].onChange) {
                nameInput[propsKey].onChange({ target: { value: 'TEST_VALUE', name: 'name' } });
                results.afterOnChange = nameInput.value;
            }
        }
        
        return results;
    }""")
    
    print(json.dumps(diag, indent=2, ensure_ascii=False))
    
    # Now try typing with Playwright and check if it works
    if diag.get('nameInputFound'):
        name_el = page.locator('input[name="name"]').first
        name_el.click(timeout=3000)
        time.sleep(0.3)
        name_el.type("تجربة الاسم", delay=50)
        time.sleep(0.5)
        
        # Check value
        val = page.evaluate("document.querySelector('input[name=\"name\"]').value")
        print(f"\nAfter Playwright type: value='{val}'")
        
        # Check React state
        react_val = page.evaluate("""() => {
            const inp = document.querySelector('input[name="name"]');
            const propsKey = Object.keys(inp).find(k => k.startsWith('__reactProps$'));
            if (propsKey) {
                return { propsValue: inp[propsKey].value, htmlValue: inp.value };
            }
            return { htmlValue: inp.value };
        }""")
        print(f"React state: {json.dumps(react_val, ensure_ascii=False)}")
    
    browser.close()
