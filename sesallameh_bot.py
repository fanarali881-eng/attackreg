#!/usr/bin/env python3
"""
sesallameh.com - Automated Appointment Booking Bot
Uses Playwright (real browser) with random Saudi data
Runs on VPS servers via FlareSolverr proxy or direct Playwright
"""

import random
import string
import time
import sys
import os
import json
import subprocess
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

PLATE_LETTERS = ['أ', 'ب', 'ح', 'د', 'ر', 'س', 'ص', 'ط', 'ع', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي']
PLATE_LETTERS_EN = ['A', 'B', 'J', 'D', 'R', 'S', 'X', 'T', 'E', 'G', 'K', 'L', 'Z', 'N', 'H', 'U', 'V']

REGIONS = [
    'منطقة الرياض', 'منطقة مكة المكرمة', 'المنطقة الشرقية', 'منطقة المدينة المنورة',
    'منطقة القصيم', 'منطقة عسير', 'منطقة تبوك', 'منطقة حائل',
    'منطقة الحدود الشمالية', 'منطقة جازان', 'منطقة نجران', 'منطقة الباحة', 'منطقة الجوف'
]

REGISTRATION_TYPES_INDEX = [1, 2, 3]  # خصوصي, نقل عام, نقل خاص
VEHICLE_TYPES_INDEX = [0, 1]  # سيارة خاصة, مركبة نقل خفيفة خاصة
SERVICE_TYPES_INDEX = [0]  # خدمة الفحص الدوري

TIMES = [
    '07:00 ص', '07:30 ص', '08:00 ص', '08:30 ص', '09:00 ص', '09:30 ص',
    '10:00 ص', '10:30 ص', '11:00 ص', '11:30 ص', '12:00 م', '12:30 م',
    '01:00 م', '01:30 م', '02:00 م', '02:30 م', '03:00 م', '03:30 م',
    '04:00 م', '04:30 م', '05:00 م', '05:30 م', '06:00 م', '06:30 م',
    '07:00 م', '07:30 م', '08:00 م', '08:30 م', '09:00 م', '09:30 م',
    '10:00 م', '10:30 م', '11:00 م'
]


def gen_saudi_id():
    """Generate a valid-looking Saudi national ID (starts with 1, 10 digits)"""
    return '1' + ''.join([str(random.randint(0, 9)) for _ in range(9)])


def gen_saudi_phone():
    """Generate Saudi phone number 05xxxxxxxx"""
    prefixes = ['50', '53', '54', '55', '56', '57', '58', '59']
    return '0' + random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(7)])


def gen_name():
    """Generate random Saudi full name"""
    if random.random() > 0.3:
        first = random.choice(SAUDI_MALE_FIRST)
    else:
        first = random.choice(SAUDI_FEMALE_FIRST)
    last = random.choice(SAUDI_LAST)
    return f"{first} {last}"


def gen_email(name):
    """Generate random email based on name"""
    domains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']
    clean = name.replace(' ', '').lower()
    num = random.randint(1, 999)
    return f"{clean}{num}@{random.choice(domains)}"


def gen_plate():
    """Generate random Saudi plate: 3 letters + 1-4 digit number"""
    letters = [random.choice(range(len(PLATE_LETTERS))) for _ in range(3)]
    number = str(random.randint(1, 9999))
    return letters, number


def gen_date():
    """Generate a future date within next 30 days"""
    days_ahead = random.randint(1, 30)
    future = datetime.now() + timedelta(days=days_ahead)
    return future.strftime('%Y-%m-%d')


def gen_time_index():
    """Generate random time slot index"""
    return random.randint(0, len(TIMES) - 1)


def gen_booking_data():
    """Generate complete random booking data"""
    name = gen_name()
    plate_letters, plate_number = gen_plate()
    return {
        'name': name,
        'national_id': gen_saudi_id(),
        'nationality_index': 0,  # السعودية
        'phone': gen_saudi_phone(),
        'email': gen_email(name),
        'vehicle_status': 'license',  # تحمل رخصة سير
        'country_index': 0,  # السعودية
        'plate_letter1': plate_letters[0] + 1,  # +1 because index 0 is "- اختر -"
        'plate_letter2': plate_letters[1] + 1,
        'plate_letter3': plate_letters[2] + 1,
        'plate_number': plate_number,
        'registration_type': random.choice(REGISTRATION_TYPES_INDEX),
        'vehicle_type': random.choice(VEHICLE_TYPES_INDEX),
        'service_type': 0,  # خدمة الفحص الدوري
        'region_index': random.randint(1, 13),  # Random region (skip index 0 = "اختر منطقة")
        'date': gen_date(),
        'time_index': gen_time_index(),
    }


# ============ PLAYWRIGHT BROWSER AUTOMATION ============

def fill_booking_form(page, data, log_fn=print):
    """Fill the sesallameh.com booking form with random data"""
    try:
        # Navigate to booking page
        log_fn(f"🌐 Opening sesallameh.com/new-appointment...")
        page.goto('https://sesallameh.com/new-appointment', wait_until='networkidle', timeout=30000)
        time.sleep(random.uniform(1, 3))

        # === PERSONAL INFO ===
        log_fn(f"📝 Filling personal info: {data['name']}")

        # Name
        name_input = page.locator('input[placeholder="إدخل الإسم"]')
        name_input.click()
        time.sleep(random.uniform(0.3, 0.8))
        name_input.fill(data['name'])
        time.sleep(random.uniform(0.3, 0.5))

        # National ID
        id_input = page.locator('input[placeholder="رقم الهوية / الإقامة"]')
        id_input.click()
        time.sleep(random.uniform(0.3, 0.8))
        id_input.fill(data['national_id'])
        time.sleep(random.uniform(0.3, 0.5))

        # Nationality - already defaults to السعودية (index 0)
        # No change needed

        # Phone
        phone_input = page.locator('input[placeholder="أكتب رقم الجوال هنا..."]')
        phone_input.click()
        time.sleep(random.uniform(0.3, 0.8))
        phone_input.fill(data['phone'])
        time.sleep(random.uniform(0.3, 0.5))

        # Email (optional but fill it)
        email_input = page.locator('input[placeholder="البريد الإلكتروني"]')
        email_input.click()
        time.sleep(random.uniform(0.3, 0.8))
        email_input.fill(data['email'])
        time.sleep(random.uniform(0.3, 0.5))

        # === VEHICLE INFO ===
        log_fn(f"🚗 Filling vehicle info...")

        # Vehicle status - click "تحمل رخصة سير" button
        license_btn = page.locator('button:has-text("تحمل رخصة سير")')
        license_btn.click()
        time.sleep(random.uniform(0.5, 1))

        # Country - already defaults to السعودية
        # No change needed

        # Plate letters (3 select dropdowns)
        plate_selects = page.locator('select').all()
        # Find the plate letter selects - they are after nationality and country selects
        # We need to identify them by their options containing "أ - A"
        plate_select_indices = []
        for i, sel in enumerate(plate_selects):
            try:
                options_text = sel.inner_text()
                if 'أ - A' in options_text and '- اختر -' in options_text:
                    plate_select_indices.append(i)
            except:
                pass

        if len(plate_select_indices) >= 3:
            # Select letter 1
            plate_selects[plate_select_indices[0]].select_option(index=data['plate_letter1'])
            time.sleep(random.uniform(0.3, 0.5))
            # Select letter 2
            plate_selects[plate_select_indices[1]].select_option(index=data['plate_letter2'])
            time.sleep(random.uniform(0.3, 0.5))
            # Select letter 3
            plate_selects[plate_select_indices[2]].select_option(index=data['plate_letter3'])
            time.sleep(random.uniform(0.3, 0.5))
        else:
            log_fn(f"⚠️ Could not find plate letter selects, found {len(plate_select_indices)}")

        # Plate number
        plate_num_input = page.locator('input[placeholder="أدخل الأرقام"]')
        plate_num_input.click()
        time.sleep(random.uniform(0.3, 0.5))
        plate_num_input.fill(data['plate_number'])
        time.sleep(random.uniform(0.3, 0.5))

        # Registration type
        reg_type_selects = page.locator('select').all()
        for sel in reg_type_selects:
            try:
                if 'أختر نوع التسجيل' in sel.inner_text():
                    sel.select_option(index=data['registration_type'])
                    time.sleep(random.uniform(0.3, 0.5))
                    break
            except:
                pass

        # Vehicle type - find select with "سيارة خاصة"
        for sel in reg_type_selects:
            try:
                text = sel.inner_text()
                if 'سيارة خاصة' in text and 'نقل ثقيل' in text:
                    sel.select_option(index=data['vehicle_type'])
                    time.sleep(random.uniform(0.3, 0.5))
                    break
            except:
                pass

        # Service type - find select with "خدمة الفحص الدوري"
        for sel in reg_type_selects:
            try:
                text = sel.inner_text()
                if 'خدمة الفحص الدوري' in text and 'خدمة إعادة الفحص' in text:
                    sel.select_option(index=data['service_type'])
                    time.sleep(random.uniform(0.3, 0.5))
                    break
            except:
                pass

        # === SERVICE CENTER ===
        log_fn(f"📍 Selecting region and center...")

        # Region
        for sel in reg_type_selects:
            try:
                text = sel.inner_text()
                if 'اختر منطقة' in text and 'منطقة الرياض' in text:
                    sel.select_option(index=data['region_index'])
                    time.sleep(random.uniform(1, 2))  # Wait for centers to load
                    break
            except:
                pass

        # Inspection center - select first available after region loads
        time.sleep(1.5)
        for sel in page.locator('select').all():
            try:
                text = sel.inner_text()
                if 'اختر مركز الفحص' in text:
                    options = sel.locator('option').all()
                    if len(options) > 1:
                        sel.select_option(index=random.randint(1, min(len(options) - 1, 5)))
                        time.sleep(random.uniform(0.5, 1))
                    break
            except:
                pass

        # === APPOINTMENT ===
        log_fn(f"📅 Setting date and time...")

        # Date
        date_input = page.locator('input[type="date"]')
        date_input.fill(data['date'])
        time.sleep(random.uniform(0.5, 1))

        # Time
        for sel in page.locator('select').all():
            try:
                text = sel.inner_text()
                if '07:00 ص' in text and '11:00 م' in text:
                    sel.select_option(index=data['time_index'])
                    time.sleep(random.uniform(0.3, 0.5))
                    break
            except:
                pass

        # === SUBMIT ===
        log_fn(f"✅ Clicking التالي (Next)...")
        time.sleep(random.uniform(0.5, 1.5))

        next_btn = page.locator('button:has-text("التالي")')
        next_btn.click()
        time.sleep(random.uniform(2, 4))

        # Check if we moved to next page
        current_url = page.url
        log_fn(f"📄 Current URL after submit: {current_url}")

        # Try to interact with next page if loaded
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
            log_fn(f"✅ Successfully submitted! Page loaded.")
        except:
            log_fn(f"⏳ Page still loading...")

        return True

    except Exception as e:
        log_fn(f"❌ Error filling form: {str(e)}")
        return False


# ============ MAIN BOT LOOP ============

def run_bot(duration_min=5, num_instances=3):
    """Run the booking bot for specified duration"""
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
    total_bookings = 0
    total_errors = 0
    status_file = '/root/sesallameh_status.json'

    def update_status():
        elapsed = time.time() - start_time
        status = {
            'status': 'running',
            'bookings': total_bookings,
            'errors': total_errors,
            'elapsed': round(elapsed, 1),
            'target_duration': duration_min * 60,
            'timestamp': time.time()
        }
        try:
            with open(status_file, 'w') as f:
                json.dump(status, f)
        except:
            pass

    print(f"🚀 Starting sesallameh bot - Duration: {duration_min} min, Instances: {num_instances}")

    with sync_playwright() as p:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            print(f"\n⏱️ Remaining: {remaining}s | Bookings: {total_bookings} | Errors: {total_errors}")

            try:
                # Launch browser
                browser_args = [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]

                browser = p.chromium.launch(
                    headless=True,
                    args=browser_args
                )

                context_opts = {
                    'viewport': {'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
                    'locale': 'ar-SA',
                    'timezone_id': 'Asia/Riyadh',
                    'user_agent': random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
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
                """)

                # Run multiple pages in parallel
                pages = []
                for i in range(num_instances):
                    if time.time() >= end_time:
                        break
                    page = context.new_page()
                    pages.append(page)

                for idx, page in enumerate(pages):
                    if time.time() >= end_time:
                        break

                    data = gen_booking_data()
                    print(f"\n👤 Instance {idx+1}: {data['name']} | {data['phone']} | ID: {data['national_id']}")

                    success = fill_booking_form(page, data, log_fn=print)
                    if success:
                        total_bookings += 1
                        print(f"✅ Booking #{total_bookings} completed!")
                    else:
                        total_errors += 1

                    update_status()

                # Cleanup
                for page in pages:
                    try:
                        page.close()
                    except:
                        pass
                context.close()
                browser.close()

            except Exception as e:
                total_errors += 1
                print(f"❌ Browser error: {str(e)}")
                update_status()
                time.sleep(2)

            # Small delay between rounds
            time.sleep(random.uniform(1, 3))

    # Final status
    elapsed = time.time() - start_time
    final_status = {
        'status': 'finished',
        'bookings': total_bookings,
        'errors': total_errors,
        'elapsed': round(elapsed, 1),
        'target_duration': duration_min * 60,
        'timestamp': time.time()
    }
    try:
        with open(status_file, 'w') as f:
            json.dump(final_status, f)
    except:
        pass

    print(f"\n🏁 FINISHED! Total bookings: {total_bookings} | Errors: {total_errors} | Time: {round(elapsed)}s")


if __name__ == '__main__':
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    instances = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run_bot(duration_min=duration, num_instances=instances)
