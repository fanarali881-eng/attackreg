#!/usr/bin/env python3
"""
Smart Universal Form Bot - Detects and fills ANY booking/registration form
Uses Playwright (real Chrome browser) + intelligent form detection
Generates random Saudi data for all field types
"""

import random
import string
import time
import sys
import os
import json
import re
from datetime import datetime, timedelta

# ============ RANDOM SAUDI DATA GENERATOR ============

SAUDI_MALE_FIRST = [
    'محمد', 'عبدالله', 'فهد', 'سعود', 'خالد', 'عبدالرحمن', 'سلطان', 'تركي',
    'بندر', 'نايف', 'فيصل', 'ماجد', 'أحمد', 'عمر', 'يوسف', 'إبراهيم',
    'عبدالعزيز', 'مشعل', 'سعد', 'حمد', 'ناصر', 'مساعد', 'راشد', 'وليد',
    'طلال', 'بدر', 'هاني', 'زياد', 'عادل', 'صالح', 'علي', 'حسن',
    'حسين', 'عبدالملك', 'منصور', 'دخيل', 'متعب', 'مشاري', 'عبدالإله', 'رائد'
]

SAUDI_FEMALE_FIRST = [
    'نورة', 'سارة', 'فاطمة', 'مريم', 'هيفاء', 'ريم', 'لمى', 'دانة',
    'العنود', 'هند', 'أمل', 'منال', 'عبير', 'لطيفة', 'موضي', 'نوف',
    'بدور', 'غادة', 'شيخة', 'حصة', 'جواهر', 'مها', 'رقية', 'خلود'
]

SAUDI_LAST = [
    'العتيبي', 'الحربي', 'القحطاني', 'الشمري', 'الدوسري', 'المطيري', 'الغامدي',
    'الزهراني', 'السبيعي', 'البقمي', 'الشهري', 'العمري', 'الأحمدي', 'الثبيتي',
    'المالكي', 'الجهني', 'البلوي', 'العنزي', 'الرشيدي', 'السهلي', 'الخالدي',
    'الحازمي', 'الفيفي', 'الشهراني', 'الأسمري', 'الوادعي', 'الكلبي', 'النفيعي',
    'السلمي', 'الثقفي', 'الطويرقي', 'الحارثي', 'الزبيدي', 'اليامي', 'المري',
    'الرويلي', 'السحيمي', 'الصاعدي', 'الحمادي', 'العلياني'
]

SAUDI_CITIES = [
    'الرياض', 'جدة', 'مكة المكرمة', 'المدينة المنورة', 'الدمام', 'الخبر',
    'الطائف', 'تبوك', 'بريدة', 'حائل', 'خميس مشيط', 'أبها', 'نجران',
    'جازان', 'ينبع', 'الجبيل', 'الأحساء', 'القطيف', 'عرعر', 'سكاكا'
]

PLATE_LETTERS_AR = ['أ', 'ب', 'ح', 'د', 'ر', 'س', 'ص', 'ط', 'ع', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي']


def gen_saudi_id():
    return '1' + ''.join([str(random.randint(0, 9)) for _ in range(9)])

def gen_iqama():
    return '2' + ''.join([str(random.randint(0, 9)) for _ in range(9)])

def gen_saudi_phone():
    prefixes = ['50', '53', '54', '55', '56', '57', '58', '59']
    return '05' + random.choice(prefixes)[1] + ''.join([str(random.randint(0, 9)) for _ in range(7)])

def gen_name():
    if random.random() > 0.3:
        first = random.choice(SAUDI_MALE_FIRST)
    else:
        first = random.choice(SAUDI_FEMALE_FIRST)
    last = random.choice(SAUDI_LAST)
    return f"{first} {last}"

def gen_first_name():
    if random.random() > 0.3:
        return random.choice(SAUDI_MALE_FIRST)
    return random.choice(SAUDI_FEMALE_FIRST)

def gen_last_name():
    return random.choice(SAUDI_LAST)

def gen_email(name=None):
    domains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']
    if name:
        clean = name.replace(' ', '').lower()
        # transliterate basic arabic
        clean = re.sub(r'[^\x00-\x7F]+', '', clean) or 'user'
    else:
        clean = 'user'
    num = random.randint(1, 9999)
    letters = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 7)))
    return f"{letters}{num}@{random.choice(domains)}"

def gen_plate_number():
    return str(random.randint(1, 9999))

def gen_plate_letters():
    return ' '.join(random.choices(PLATE_LETTERS_AR, k=3))

def gen_date_future(days_min=1, days_max=30):
    days_ahead = random.randint(days_min, days_max)
    future = datetime.now() + timedelta(days=days_ahead)
    return future.strftime('%Y-%m-%d')

def gen_date_birth():
    year = random.randint(1970, 2002)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"

def gen_city():
    return random.choice(SAUDI_CITIES)

def gen_address():
    return f"شارع {random.choice(['الملك فهد', 'الملك عبدالعزيز', 'الأمير سلطان', 'التحلية', 'العليا', 'الثلاثين', 'الستين', 'الخمسين'])}، حي {random.choice(['النزهة', 'الروضة', 'السلامة', 'الحمراء', 'المروج', 'الياسمين', 'الملقا', 'العقيق'])}"

def gen_postal_code():
    return str(random.randint(10000, 99999))

def gen_number_string(length=4):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


# ============ SMART FIELD DETECTION ============

# Keywords that help identify what type of data a field expects
FIELD_PATTERNS = {
    'name': {
        'keywords': ['اسم', 'الاسم', 'name', 'الإسم', 'اسمك', 'الاسم الكامل', 'full name', 'your name', 'اسم المستخدم'],
        'generator': gen_name
    },
    'first_name': {
        'keywords': ['الاسم الأول', 'first name', 'الاسم الاول', 'اسم اول'],
        'generator': gen_first_name
    },
    'last_name': {
        'keywords': ['اسم العائلة', 'last name', 'اللقب', 'الاسم الأخير', 'family name', 'surname'],
        'generator': gen_last_name
    },
    'national_id': {
        'keywords': ['هوية', 'الهوية', 'رقم الهوية', 'national id', 'id number', 'إقامة', 'الإقامة', 'هوية / إقامة', 'هوية/اقامة', 'identity', 'civil id'],
        'generator': gen_saudi_id
    },
    'phone': {
        'keywords': ['جوال', 'الجوال', 'هاتف', 'الهاتف', 'phone', 'mobile', 'رقم الجوال', 'رقم الهاتف', 'تلفون', 'موبايل', 'cell'],
        'generator': gen_saudi_phone
    },
    'email': {
        'keywords': ['بريد', 'إيميل', 'email', 'البريد', 'بريد إلكتروني', 'البريد الإلكتروني', 'e-mail', 'mail'],
        'generator': gen_email
    },
    'date': {
        'keywords': ['تاريخ', 'date', 'موعد', 'التاريخ', 'تاريخ الموعد', 'appointment date'],
        'generator': gen_date_future
    },
    'birth_date': {
        'keywords': ['تاريخ الميلاد', 'birth date', 'date of birth', 'الميلاد', 'dob', 'birthday'],
        'generator': gen_date_birth
    },
    'city': {
        'keywords': ['مدينة', 'المدينة', 'city', 'البلد', 'المنطقة'],
        'generator': gen_city
    },
    'address': {
        'keywords': ['عنوان', 'العنوان', 'address', 'الحي', 'الشارع', 'street'],
        'generator': gen_address
    },
    'postal_code': {
        'keywords': ['رمز بريدي', 'postal', 'zip', 'الرمز البريدي', 'zip code', 'postal code'],
        'generator': gen_postal_code
    },
    'plate_number': {
        'keywords': ['لوحة', 'اللوحة', 'plate', 'رقم اللوحة', 'أرقام', 'plate number'],
        'generator': gen_plate_number
    },
}


def detect_field_type(element_info):
    """Detect what type of data a form field expects based on its attributes"""
    # Combine all text clues: placeholder, label, name, id, aria-label
    clues = ' '.join([
        element_info.get('placeholder', ''),
        element_info.get('label', ''),
        element_info.get('name', ''),
        element_info.get('id', ''),
        element_info.get('aria_label', ''),
        element_info.get('nearby_text', ''),
    ]).lower()

    # Check input type first
    input_type = element_info.get('type', 'text').lower()
    if input_type == 'email':
        return 'email'
    if input_type == 'tel':
        return 'phone'
    if input_type == 'date':
        return 'date'
    if input_type == 'number':
        # Could be phone, ID, plate number, etc.
        for field_type, patterns in FIELD_PATTERNS.items():
            for kw in patterns['keywords']:
                if kw in clues:
                    return field_type
        return 'generic_number'

    # Match against keyword patterns
    best_match = None
    best_score = 0
    for field_type, patterns in FIELD_PATTERNS.items():
        for kw in patterns['keywords']:
            if kw in clues:
                score = len(kw)  # Longer match = more specific
                if score > best_score:
                    best_score = score
                    best_match = field_type

    return best_match or 'generic_text'


def generate_value_for_field(field_type):
    """Generate appropriate random Saudi data for detected field type"""
    if field_type in FIELD_PATTERNS:
        return FIELD_PATTERNS[field_type]['generator']()
    elif field_type == 'generic_number':
        return gen_number_string(random.randint(4, 8))
    elif field_type == 'generic_text':
        # Random Arabic text
        return random.choice([gen_name(), gen_city(), gen_address()])
    return ''


# ============ PLAYWRIGHT SMART FORM FILLER ============

def smart_fill_page(page, target_url, log_fn=print):
    """
    Smart form filler - detects all form fields on any page and fills them
    with appropriate random Saudi data
    """
    try:
        log_fn(f"🌐 Opening {target_url}...")
        page.goto(target_url, wait_until='networkidle', timeout=45000)
        time.sleep(random.uniform(2, 4))

        # Simulate human behavior - scroll down slowly
        page.mouse.move(random.randint(100, 500), random.randint(100, 300))
        time.sleep(random.uniform(0.5, 1))

        filled_count = 0
        selected_count = 0
        clicked_count = 0

        # ===== STEP 1: Detect and fill text inputs =====
        log_fn("🔍 Scanning form fields...")

        inputs = page.locator('input:visible').all()
        for inp in inputs:
            try:
                input_type = (inp.get_attribute('type') or 'text').lower()
                if input_type in ['hidden', 'submit', 'button', 'image', 'file', 'checkbox', 'radio']:
                    continue

                # Gather clues about this field
                element_info = {
                    'type': input_type,
                    'placeholder': inp.get_attribute('placeholder') or '',
                    'name': inp.get_attribute('name') or '',
                    'id': inp.get_attribute('id') or '',
                    'aria_label': inp.get_attribute('aria-label') or '',
                    'nearby_text': '',
                }

                # Try to find associated label
                field_id = inp.get_attribute('id')
                if field_id:
                    try:
                        label = page.locator(f'label[for="{field_id}"]')
                        if label.count() > 0:
                            element_info['label'] = label.first.inner_text()
                    except:
                        pass

                # Try to get nearby text (parent or sibling)
                try:
                    parent_text = inp.evaluate('el => el.parentElement ? el.parentElement.innerText : ""')
                    element_info['nearby_text'] = parent_text[:200] if parent_text else ''
                except:
                    pass

                # Detect field type
                field_type = detect_field_type(element_info)
                value = generate_value_for_field(field_type)

                if value:
                    # Human-like typing
                    inp.click()
                    time.sleep(random.uniform(0.2, 0.5))
                    inp.fill('')
                    time.sleep(random.uniform(0.1, 0.3))

                    if input_type == 'date':
                        inp.fill(value)
                    else:
                        # Type character by character for more human-like behavior
                        if len(value) <= 20:
                            for char in value:
                                inp.type(char, delay=random.randint(30, 100))
                        else:
                            inp.fill(value)

                    filled_count += 1
                    log_fn(f"  ✅ [{field_type}] = {value}")
                    time.sleep(random.uniform(0.2, 0.5))

            except Exception as e:
                log_fn(f"  ⚠️ Skip input: {str(e)[:50]}")
                continue

        # ===== STEP 2: Handle textareas =====
        textareas = page.locator('textarea:visible').all()
        for ta in textareas:
            try:
                ta.click()
                time.sleep(random.uniform(0.2, 0.5))
                text = random.choice([
                    'أرغب في حجز موعد',
                    'طلب حجز موعد جديد',
                    'حجز موعد فحص',
                    gen_address(),
                ])
                ta.fill(text)
                filled_count += 1
                log_fn(f"  ✅ [textarea] = {text[:30]}...")
            except:
                continue

        # ===== STEP 3: Handle select dropdowns =====
        selects = page.locator('select:visible').all()
        for sel in selects:
            try:
                options = sel.locator('option').all()
                if len(options) > 1:
                    # Skip first option if it's a placeholder (اختر, -- , select)
                    start_idx = 0
                    try:
                        first_text = options[0].inner_text().strip()
                        if any(kw in first_text.lower() for kw in ['اختر', 'اختار', 'select', '--', '- -', 'choose', 'الكل']):
                            start_idx = 1
                    except:
                        start_idx = 1

                    if start_idx < len(options):
                        idx = random.randint(start_idx, min(len(options) - 1, start_idx + 5))
                        sel.select_option(index=idx)
                        selected_count += 1
                        try:
                            selected_text = options[idx].inner_text().strip()
                            log_fn(f"  ✅ [select] = {selected_text[:30]}")
                        except:
                            log_fn(f"  ✅ [select] index={idx}")
                        time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                log_fn(f"  ⚠️ Skip select: {str(e)[:50]}")
                continue

        # ===== STEP 4: Handle radio buttons =====
        radio_groups = {}
        radios = page.locator('input[type="radio"]:visible').all()
        for radio in radios:
            try:
                name = radio.get_attribute('name') or 'unnamed'
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)
            except:
                continue

        for name, group in radio_groups.items():
            try:
                choice = random.choice(group)
                choice.click()
                clicked_count += 1
                log_fn(f"  ✅ [radio:{name}] clicked")
                time.sleep(random.uniform(0.3, 0.7))
            except:
                continue

        # ===== STEP 5: Handle checkboxes (check them) =====
        checkboxes = page.locator('input[type="checkbox"]:visible').all()
        for cb in checkboxes:
            try:
                if not cb.is_checked():
                    cb.click()
                    clicked_count += 1
                    log_fn(f"  ✅ [checkbox] checked")
                    time.sleep(random.uniform(0.2, 0.5))
            except:
                continue

        log_fn(f"📊 Filled: {filled_count} inputs | {selected_count} selects | {clicked_count} clicks")

        # ===== STEP 6: Find and click submit/next button =====
        time.sleep(random.uniform(1, 2))

        submit_keywords = [
            'التالي', 'تالي', 'إرسال', 'ارسال', 'حجز', 'تأكيد', 'تسجيل', 'إتمام', 'اتمام',
            'submit', 'next', 'book', 'confirm', 'register', 'send', 'continue',
            'حفظ', 'save', 'تقديم', 'موافق', 'ok', 'proceed', 'احجز', 'سجل',
            'ابدأ', 'بدء', 'start', 'go', 'متابعة'
        ]

        submitted = False

        # Try buttons first
        buttons = page.locator('button:visible').all()
        for btn in buttons:
            try:
                btn_text = btn.inner_text().strip().lower()
                btn_type = (btn.get_attribute('type') or '').lower()

                # Skip if it's clearly not a submit button
                if any(skip in btn_text for skip in ['إلغاء', 'cancel', 'رجوع', 'back', 'مسح', 'clear']):
                    continue

                for kw in submit_keywords:
                    if kw in btn_text or btn_type == 'submit':
                        log_fn(f"🖱️ Clicking button: '{btn_text[:30]}'")
                        btn.click()
                        submitted = True
                        break
                if submitted:
                    break
            except:
                continue

        # If no button found, try input[type=submit]
        if not submitted:
            try:
                submit_input = page.locator('input[type="submit"]:visible').first
                if submit_input:
                    log_fn(f"🖱️ Clicking submit input")
                    submit_input.click()
                    submitted = True
            except:
                pass

        # If still no submit, try any prominent button/link
        if not submitted:
            try:
                # Try links that look like buttons
                links = page.locator('a:visible').all()
                for link in links:
                    try:
                        link_text = link.inner_text().strip().lower()
                        for kw in submit_keywords:
                            if kw in link_text:
                                log_fn(f"🖱️ Clicking link: '{link_text[:30]}'")
                                link.click()
                                submitted = True
                                break
                        if submitted:
                            break
                    except:
                        continue
            except:
                pass

        if submitted:
            time.sleep(random.uniform(3, 5))
            try:
                page.wait_for_load_state('networkidle', timeout=15000)
            except:
                pass
            current_url = page.url
            log_fn(f"📄 After submit URL: {current_url}")

            # Try to fill the next page too if there are more forms
            next_inputs = page.locator('input:visible').count()
            next_selects = page.locator('select:visible').count()
            if next_inputs > 0 or next_selects > 0:
                log_fn(f"📋 Next page has {next_inputs} inputs, {next_selects} selects - filling...")
                # Recursively fill next page (max 1 level deep to avoid infinite loops)
                return True, True  # success, has_next_page
            return True, False
        else:
            log_fn("⚠️ No submit button found")
            return True, False

    except Exception as e:
        log_fn(f"❌ Error: {str(e)}")
        return False, False


# ============ MAIN BOT LOOP ============

def run_smart_bot(target_url, duration_min=5, num_instances=3):
    """Run the smart form bot for specified duration on any URL"""
    from playwright.sync_api import sync_playwright

    proxy_user = os.environ.get('PROXY_USER', '')
    proxy_pass = os.environ.get('PROXY_PASS', '')
    proxy_host = os.environ.get('PROXY_HOST', 'proxy.packetstream.io')
    proxy_port = os.environ.get('PROXY_PORT', '31112')

    proxy_config = None
    if proxy_user and proxy_pass:
        proxy_config = {
            'server': f'http://{proxy_host}:{proxy_port}',
            'username': proxy_user,
            'password': proxy_pass
        }
        print(f"🌐 Using proxy: {proxy_host}:{proxy_port} ({proxy_user})")

    start_time = time.time()
    end_time = start_time + (duration_min * 60)
    total_submissions = 0
    total_errors = 0
    status_file = '/root/smart_bot_status.json'

    def update_status(status='running'):
        elapsed = time.time() - start_time
        data = {
            'status': status,
            'submissions': total_submissions,
            'errors': total_errors,
            'elapsed': round(elapsed, 1),
            'target_duration': duration_min * 60,
            'target_url': target_url,
            'timestamp': time.time()
        }
        try:
            with open(status_file, 'w') as f:
                json.dump(data, f)
        except:
            pass

    print(f"🚀 Smart Bot starting - URL: {target_url} | Duration: {duration_min}min | Instances: {num_instances}")
    update_status()

    with sync_playwright() as p:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            print(f"\n⏱️ Remaining: {remaining}s | Submissions: {total_submissions} | Errors: {total_errors}")

            try:
                browser_args = [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]

                browser = p.chromium.launch(headless=True, args=browser_args)

                context_opts = {
                    'viewport': {'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
                    'locale': 'ar-SA',
                    'timezone_id': 'Asia/Riyadh',
                    'user_agent': random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
                        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
                    ]),
                }

                if proxy_config:
                    context_opts['proxy'] = proxy_config

                context = browser.new_context(**context_opts)

                # Anti-detection
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'languages', { get: () => ['ar-SA', 'ar', 'en-US', 'en'] });
                    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                    window.chrome = { runtime: {} };
                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)

                # Run instances
                for i in range(num_instances):
                    if time.time() >= end_time:
                        break

                    page = context.new_page()
                    print(f"\n👤 Instance {i+1}/{num_instances}")

                    success, has_next = smart_fill_page(page, target_url, log_fn=print)

                    if success:
                        total_submissions += 1
                        print(f"✅ Submission #{total_submissions} completed!")

                        # If there's a next page, fill it too
                        if has_next:
                            print("📋 Filling next page...")
                            success2, _ = smart_fill_page(page, page.url, log_fn=print)
                            if success2:
                                print("✅ Next page also filled!")
                    else:
                        total_errors += 1

                    update_status()

                    try:
                        page.close()
                    except:
                        pass

                    time.sleep(random.uniform(1, 3))

                context.close()
                browser.close()

            except Exception as e:
                total_errors += 1
                print(f"❌ Browser error: {str(e)}")
                update_status()
                time.sleep(3)

            time.sleep(random.uniform(1, 3))

    # Final
    elapsed = time.time() - start_time
    update_status('finished')
    print(f"\n🏁 FINISHED! Submissions: {total_submissions} | Errors: {total_errors} | Time: {round(elapsed)}s")


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://sesallameh.com/new-appointment'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    instances = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    run_smart_bot(target_url=url, duration_min=duration, num_instances=instances)
