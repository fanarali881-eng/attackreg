"""
Smart Universal Form Bot v25 - Patchright-powered Cloudflare bypass
Uses Patchright (undetected Chrome) + smart placeholder-based form detection
Bypasses Cloudflare Turnstile by clicking the checkbox with Patchright's stealth
Generates random Saudi data, fills registration + payment forms
"""

import random
import string
import time
import sys
import os
import json
import re
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urlparse

os.environ.setdefault('DISPLAY', ':99')

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

SAUDI_BANK_BINS = {
    'Al Rajhi': ['554575', '968205', '458838', '458837', '468564', '468565'],
    'Al Ahli (NCB)': ['554180', '556676', '556675', '588850', '968202', '417633', '417634'],
    'Riyad Bank': ['559322', '558563', '968209', '454313', '454314', '489318'],
    'SABB': ['422818', '422819', '605141', '968204', '431361'],
    'Saudi Fransi': ['440795', '552360', '588845', '968208', '440647'],
    'Arab National Bank': ['455036', '455037', '549400', '588848', '968203'],
    'Alinma Bank': ['552363', '968206', '426897', '485457'],
    'Bank Al-Jazira': ['445564', '968211', '409201'],
    'Saudi Investment Bank': ['552384', '589206', '968207'],
    'Samba': ['552250', '552089', '446392', '446672'],
    'Al Bilad Bank': ['636120', '968201', '468540'],
    'Alawwal Bank': ['552438', '552375', '558854', '558848', '557606', '548979', '512060'],
}


def _validate_saudi_id(identifier):
    """Validate Saudi ID using official algorithm"""
    if not identifier.isdigit() or len(identifier) != 10 or identifier[0] not in ('1', '2'):
        return -1
    checksum = 0
    for digit, num in enumerate(identifier):
        num = int(num)
        checksum += sum(map(int, str(num * 2))) if digit % 2 == 0 else num
    return identifier[0] if checksum % 10 == 0 else -1

def gen_saudi_id():
    """Generate a valid Saudi national ID (starts with 1) that passes checksum validation"""
    while True:
        digits = [1] + [random.randint(0, 9) for _ in range(8)]
        for last in range(10):
            candidate = ''.join(str(d) for d in digits) + str(last)
            if _validate_saudi_id(candidate) != -1:
                return candidate

def gen_iqama():
    """Generate a valid Iqama number (starts with 2)"""
    while True:
        digits = [2] + [random.randint(0, 9) for _ in range(8)]
        for last in range(10):
            candidate = ''.join(str(d) for d in digits) + str(last)
            if _validate_saudi_id(candidate) != -1:
                return candidate

def gen_saudi_phone():
    prefixes = ['50', '53', '54', '55', '56', '57', '58', '59']
    return '05' + random.choice(prefixes)[1] + ''.join([str(random.randint(0, 9)) for _ in range(7)])

def gen_name():
    first = random.choice(SAUDI_MALE_FIRST if random.random() > 0.3 else SAUDI_FEMALE_FIRST)
    last = random.choice(SAUDI_LAST)
    return f"{first} {last}"

def gen_email():
    user = ''.join(random.choices(string.ascii_lowercase, k=random.randint(6, 10)))
    user += str(random.randint(1, 999))
    return f"{user}@{random.choice(['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com'])}"

def gen_plate_number():
    return str(random.randint(1, 9999))

def gen_card_number():
    bank_name = random.choice(list(SAUDI_BANK_BINS.keys()))
    bin_prefix = random.choice(SAUDI_BANK_BINS[bank_name])
    remaining_length = 15 - len(bin_prefix)
    digits = [int(d) for d in bin_prefix] + [random.randint(0, 9) for _ in range(remaining_length)]
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == 0:
            doubled = d * 2
            total += doubled - 9 if doubled > 9 else doubled
        else:
            total += d
    check = (10 - (total % 10)) % 10
    digits.append(check)
    return ''.join(str(d) for d in digits), bank_name

def gen_card_expiry():
    month = f"{random.randint(1, 12):02d}"
    year = str(random.randint(2027, 2030))
    return f"{month}/{year[-2:]}"

def gen_card_expiry_month():
    return f"{random.randint(1, 12):02d}"

def gen_card_expiry_year():
    return str(random.randint(2027, 2030))

def gen_cvv():
    return str(random.randint(100, 999))

def gen_cardholder_name():
    first_en = random.choice(['Mohammed', 'Abdullah', 'Fahad', 'Saud', 'Khalid', 'Sultan', 'Turki', 'Bandar', 'Faisal', 'Ahmad', 'Omar', 'Youssef', 'Ibrahim', 'Nasser', 'Saad', 'Majed', 'Nayef', 'Mishari', 'Hamad', 'Ali'])
    last_en = random.choice(['Alotaibi', 'Alharbi', 'Alqahtani', 'Alshamri', 'Aldosari', 'Almutairi', 'Alghamdi', 'Alzahrani', 'Alsubaie', 'Alshehri', 'Aljohani', 'Alanazi', 'Alrashidi', 'Almalki', 'Albulawi', 'Alsalmi'])
    return f"{first_en} {last_en}"


# ============ SMART FILL HELPERS ============

def fill_by_placeholder(page, placeholder, value, exact=False):
    """Fill input by its placeholder text using Playwright .fill()"""
    try:
        if exact:
            el = page.locator(f'input[placeholder="{placeholder}"]').first
        else:
            el = page.locator(f'input[placeholder*="{placeholder}"]').first
        if el.is_visible():
            el.click()
            time.sleep(random.uniform(0.2, 0.5))
            el.fill(value)
            time.sleep(random.uniform(0.1, 0.3))
            return True
    except:
        pass
    return False

def type_by_placeholder(page, placeholder, value, exact=False):
    """Type into input by placeholder (human-like, character by character)"""
    try:
        if exact:
            el = page.locator(f'input[placeholder="{placeholder}"]').first
        else:
            el = page.locator(f'input[placeholder*="{placeholder}"]').first
        if el.is_visible():
            el.click()
            time.sleep(random.uniform(0.2, 0.5))
            el.fill('')
            for ch in value:
                el.type(ch, delay=random.randint(30, 80))
            time.sleep(random.uniform(0.1, 0.3))
            return True
    except:
        pass
    return False

def select_by_prev_label(page, label_text, option_value=None):
    """Select dropdown option by the label that precedes it"""
    try:
        result = page.evaluate("""(args) => {
            const [labelText, optionValue] = args;
            const labels = document.querySelectorAll('label');
            for (const label of labels) {
                if (label.innerText.trim().includes(labelText)) {
                    let next = label.nextElementSibling;
                    while (next) {
                        if (next.tagName === 'SELECT') {
                            const opts = Array.from(next.options).filter(o => o.value && o.value !== '' && o.value !== '-' && !o.text.includes('اختر'));
                            if (opts.length === 0) return null;
                            if (optionValue) {
                                for (const opt of opts) {
                                    if (opt.value === optionValue || opt.text.includes(optionValue)) {
                                        next.value = opt.value;
                                        next.dispatchEvent(new Event('change', { bubbles: true }));
                                        return opt.text.substring(0, 30);
                                    }
                                }
                            }
                            const choice = opts[Math.floor(Math.random() * opts.length)];
                            next.value = choice.value;
                            next.dispatchEvent(new Event('change', { bubbles: true }));
                            return choice.text.substring(0, 30);
                        }
                        const sel = next.querySelector('select');
                        if (sel) {
                            const opts = Array.from(sel.options).filter(o => o.value && o.value !== '' && o.value !== '-' && !o.text.includes('اختر'));
                            if (opts.length === 0) return null;
                            if (optionValue) {
                                for (const opt of opts) {
                                    if (opt.value === optionValue || opt.text.includes(optionValue)) {
                                        sel.value = opt.value;
                                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                                        return opt.text.substring(0, 30);
                                    }
                                }
                            }
                            const choice = opts[Math.floor(Math.random() * opts.length)];
                            sel.value = choice.value;
                            sel.dispatchEvent(new Event('change', { bubbles: true }));
                            return choice.text.substring(0, 30);
                        }
                        next = next.nextElementSibling;
                    }
                    const container = label.closest('.mb-4, .form-group, div') || label.parentElement;
                    if (container) {
                        const sel = container.querySelector('select');
                        if (sel) {
                            const opts = Array.from(sel.options).filter(o => o.value && o.value !== '' && o.value !== '-' && !o.text.includes('اختر'));
                            if (opts.length === 0) return null;
                            if (optionValue) {
                                for (const opt of opts) {
                                    if (opt.value === optionValue || opt.text.includes(optionValue)) {
                                        sel.value = opt.value;
                                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                                        return opt.text.substring(0, 30);
                                    }
                                }
                            }
                            const choice = opts[Math.floor(Math.random() * opts.length)];
                            sel.value = choice.value;
                            sel.dispatchEvent(new Event('change', { bubbles: true }));
                            return choice.text.substring(0, 30);
                        }
                    }
                }
            }
            return null;
        }""", [label_text, option_value])
        return result
    except:
        return None


# ============ CLOUDFLARE BYPASS ============

def bypass_cloudflare(page, max_wait=90):
    """Bypass Cloudflare challenge using Patchright's stealth + Turnstile clicking"""
    print("  🔓 Bypassing Cloudflare...", flush=True)
    start = time.time()
    
    for i in range(int(max_wait / 3)):
        elapsed = int(time.time() - start)
        if elapsed > max_wait:
            break
        
        time.sleep(3)
        try:
            t = page.title()
        except:
            t = ''
        
        # Check if challenge is solved
        if t and 'moment' not in t.lower() and 'لحظة' not in t and 'just' not in t.lower():
            print(f"  ✅ CF bypassed ({elapsed}s) - Title: {t[:40]}", flush=True)
            return True
        
        # Every 3rd iteration, try clicking the Turnstile checkbox
        if i % 3 == 0 and i > 0:
            try:
                # Move mouse naturally then click checkbox area
                page.mouse.move(random.randint(400, 600), random.randint(300, 500))
                time.sleep(random.uniform(0.3, 0.8))
                page.mouse.move(170, 275)
                time.sleep(random.uniform(0.3, 0.6))
                page.mouse.click(170, 275)
                print(f"  🖱️ Clicked Turnstile ({elapsed}s)", flush=True)
            except:
                pass
            
            # Wait after click for verification
            time.sleep(8)
            try:
                t2 = page.title()
                if t2 and 'moment' not in t2.lower() and 'لحظة' not in t2 and 'just' not in t2.lower():
                    elapsed2 = int(time.time() - start)
                    print(f"  ✅ CF bypassed after click ({elapsed2}s) - Title: {t2[:40]}", flush=True)
                    return True
            except:
                pass
    
    elapsed = int(time.time() - start)
    print(f"  ❌ CF timeout after {elapsed}s", flush=True)
    return False


# ============ FILL REGISTRATION FORM ============

def fill_registration_form(page):
    """Fill the alamsallameh.com registration form using placeholder-based detection"""
    print("  📝 Filling registration form...", flush=True)
    
    data = {
        'name': gen_name(),
        'national_id': gen_saudi_id(),
        'phone': gen_saudi_phone(),
        'email': gen_email(),
        'plate_num': gen_plate_number(),
    }
    print(f"  📝 Data: {data['name']} | {data['national_id']} | {data['phone']} | {data['email']}", flush=True)
    
    filled = 0
    time.sleep(2)
    
    # 1. الإسم
    if fill_by_placeholder(page, 'إدخل الإسم', data['name']):
        filled += 1
        print(f"    ✅ الإسم: {data['name']}", flush=True)
    elif fill_by_placeholder(page, 'الاسم', data['name']):
        filled += 1
        print(f"    ✅ الإسم (alt): {data['name']}", flush=True)
    else:
        print(f"    ❌ الإسم", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 2. رقم الهوية
    if fill_by_placeholder(page, 'رقم الهوية', data['national_id']):
        filled += 1
        print(f"    ✅ الهوية: {data['national_id']}", flush=True)
    elif fill_by_placeholder(page, 'الهوية', data['national_id']):
        filled += 1
        print(f"    ✅ الهوية (alt): {data['national_id']}", flush=True)
    else:
        print(f"    ❌ الهوية", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 3. الجنسية
    result = select_by_prev_label(page, 'الجنسية', 'السعودية')
    if result:
        filled += 1
        print(f"    ✅ الجنسية: {result}", flush=True)
    else:
        filled += 1
        print(f"    ⚠️ الجنسية (default السعودية)", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 4. رقم الجوال
    if fill_by_placeholder(page, 'أكتب رقم الجوال', data['phone']):
        filled += 1
        print(f"    ✅ الجوال: {data['phone']}", flush=True)
    elif fill_by_placeholder(page, 'رقم الجوال', data['phone']):
        filled += 1
        print(f"    ✅ الجوال (alt): {data['phone']}", flush=True)
    else:
        try:
            el = page.locator('input.flex-1').first
            if el.is_visible():
                el.click()
                time.sleep(0.3)
                el.fill(data['phone'])
                filled += 1
                print(f"    ✅ الجوال (class): {data['phone']}", flush=True)
        except:
            # Last resort: find input near phone icon/label
            try:
                el = page.locator('input[type="tel"]').first
                if el.is_visible():
                    el.click()
                    time.sleep(0.3)
                    el.fill(data['phone'])
                    filled += 1
                    print(f"    ✅ الجوال (type=tel): {data['phone']}", flush=True)
            except:
                print(f"    ❌ الجوال", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 5. البريد الإلكتروني
    if fill_by_placeholder(page, 'البريد الإلكتروني', data['email']):
        filled += 1
        print(f"    ✅ الإيميل: {data['email']}", flush=True)
    else:
        try:
            el = page.locator('input[type="email"]').first
            if el.is_visible():
                el.click()
                time.sleep(0.3)
                el.fill(data['email'])
                filled += 1
                print(f"    ✅ الإيميل (type): {data['email']}", flush=True)
        except:
            print(f"    ❌ الإيميل", flush=True)
    time.sleep(random.uniform(0.5, 1))
    
    # 6. حالة المركبة - click "تحمل رخصة سير"
    try:
        btn = page.get_by_text("تحمل رخصة سير")
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            filled += 1
            print(f"    ✅ حالة المركبة: رخصة سير", flush=True)
            time.sleep(random.uniform(0.5, 1))
    except:
        pass
    
    # 7. بلد التسجيل
    result = select_by_prev_label(page, 'بلد التسجيل', 'السعودية')
    if result:
        filled += 1
        print(f"    ✅ بلد التسجيل: {result}", flush=True)
    else:
        filled += 1
        print(f"    ⚠️ بلد التسجيل (default)", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 8. حروف اللوحة (3 selects)
    try:
        plate_result = page.evaluate("""() => {
            const results = [];
            const selects = document.querySelectorAll('select');
            let plateCount = 0;
            for (const sel of selects) {
                const opts = Array.from(sel.options);
                const hasLetters = opts.some(o => o.text.includes(' - ') && o.text.length < 10);
                if (hasLetters && plateCount < 3) {
                    const validOpts = opts.filter(o => o.value && o.value !== '' && o.value !== '-');
                    if (validOpts.length > 0) {
                        const choice = validOpts[Math.floor(Math.random() * validOpts.length)];
                        sel.value = choice.value;
                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                        results.push(choice.text.substring(0, 8));
                        plateCount++;
                    }
                }
            }
            return results;
        }""")
        if plate_result:
            filled += len(plate_result)
            for r in plate_result:
                print(f"    ✅ حرف لوحة: {r}", flush=True)
    except:
        pass
    time.sleep(random.uniform(0.3, 0.6))
    
    # 9. أرقام اللوحة
    plate_digits = data['plate_num'].zfill(4)
    page.evaluate("window.scrollTo(0, 600)")
    time.sleep(0.5)
    plate_filled = False
    
    if fill_by_placeholder(page, 'أدخل الأرقام', plate_digits):
        filled += 1
        plate_filled = True
        print(f"    ✅ أرقام اللوحة: {plate_digits}", flush=True)
    
    if not plate_filled:
        try:
            el = page.locator('input[maxlength="4"]').first
            if el.is_visible():
                el.click()
                time.sleep(0.3)
                el.fill(plate_digits)
                filled += 1
                plate_filled = True
                print(f"    ✅ أرقام اللوحة (maxlen): {plate_digits}", flush=True)
        except:
            pass
    
    if not plate_filled:
        try:
            el = page.locator('input[placeholder*="الأرقام"]').first
            if el.is_visible():
                el.click()
                time.sleep(0.3)
                page.keyboard.type(plate_digits, delay=100)
                filled += 1
                plate_filled = True
                print(f"    ✅ أرقام اللوحة (keyboard): {plate_digits}", flush=True)
        except:
            pass
    
    if not plate_filled:
        try:
            result = page.evaluate("""(digits) => {
                const inp = document.querySelector('input[placeholder*="الأرقام"], input[maxlength="4"]');
                if (inp) {
                    inp.focus();
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(inp, digits);
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'js:' + digits;
                }
                return null;
            }""", plate_digits)
            if result:
                filled += 1
                plate_filled = True
                print(f"    ✅ أرقام اللوحة (JS): {result}", flush=True)
        except:
            pass
    
    if not plate_filled:
        print(f"    ❌ أرقام اللوحة", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 10. نوع التسجيل
    reg_types = ['خصوصي', 'نقل خاص', 'نقل عام', 'حافلة صغيرة', 'مركبة أجرة']
    result = select_by_prev_label(page, 'نوع التسجيل', random.choice(reg_types))
    if result:
        filled += 1
        print(f"    ✅ نوع التسجيل: {result}", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 11. نوع المركبة
    result = select_by_prev_label(page, 'نوع المركبة', None)
    if result:
        filled += 1
        print(f"    ✅ نوع المركبة: {result}", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 12. خدمة الفحص (default)
    filled += 1
    print(f"    ✅ خدمة الفحص: الدوري (default)", flush=True)
    
    # 13. المنطقة
    result = select_by_prev_label(page, 'المنطقة', None)
    if result:
        filled += 1
        print(f"    ✅ المنطقة: {result}", flush=True)
        time.sleep(random.uniform(1, 2))
        
        # 14. مركز الفحص
        result2 = select_by_prev_label(page, 'مركز الفحص', None)
        if result2:
            filled += 1
            print(f"    ✅ مركز الفحص: {result2}", flush=True)
    time.sleep(random.uniform(0.3, 0.6))
    
    # 15. تاريخ الفحص (default today)
    filled += 1
    print(f"    ✅ تاريخ الفحص: today (default)", flush=True)
    
    # 16. وقت الفحص
    result = select_by_prev_label(page, 'وقت الفحص', None)
    if result:
        filled += 1
        print(f"    ✅ وقت الفحص: {result}", flush=True)
    else:
        filled += 1
        print(f"    ✅ وقت الفحص: default", flush=True)
    
    print(f"  📊 Total fields filled: {filled}", flush=True)
    return filled, data


# ============ FILL PAYMENT ============

def fill_payment(page):
    """Handle full payment flow: close popup -> select card -> continue -> fill card -> pay"""
    print("  💳 Starting payment flow...", flush=True)
    
    card_num, bank = gen_card_number()
    exp_month = gen_card_expiry_month()
    exp_year = gen_card_expiry_year()
    cvv = gen_cvv()
    holder = gen_cardholder_name()
    
    print(f"  💳 Card: {card_num[:4]}****{card_num[-4:]} ({bank}) | {exp_month}/{exp_year} | {holder}", flush=True)
    
    card_data = {
        'card_number': card_num,
        'card_expiry': f"{exp_month}/{exp_year[-2:]}",
        'card_cvv': cvv,
        'card_holder': holder,
        'bank': bank,
    }
    
    # A: Close popup
    try:
        close_btn = page.get_by_text('إغلاق', exact=True)
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click()
            print("    ✅ Closed popup", flush=True)
            time.sleep(random.uniform(1, 2))
    except:
        pass
    
    # B: Select بطاقة ائتمان / مدى
    for text in ['بطاقة ائتمان', 'مدى', 'بطاقة ائتمان / مدى', 'Visa', 'MasterCard']:
        try:
            el = page.get_by_text(text)
            if el.count() > 0 and el.first.is_visible():
                el.first.click()
                print(f"    ✅ Selected: {text}", flush=True)
                time.sleep(random.uniform(1, 2))
                break
        except:
            continue
    
    # C: Click متابعة الدفع
    for text in ['متابعة الدفع', 'متابعة', 'استمرار', 'Continue']:
        try:
            btn = page.get_by_text(text)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                print(f"    ✅ Clicked: {text}", flush=True)
                time.sleep(random.uniform(5, 8))
                break
        except:
            continue
    
    print(f"  💳 Payment URL: {page.url}", flush=True)
    
    # D: Fill card fields
    filled = 0
    
    for target in [page] + [f for f in page.frames if f != page.main_frame]:
        try:
            inputs = target.locator('input:visible').all()
            if len(inputs) == 0:
                continue
            
            print(f"    🔍 Found {len(inputs)} inputs in {'main page' if target == page else 'iframe'}", flush=True)
            
            for inp in inputs:
                try:
                    itype = (inp.get_attribute('type') or 'text').lower()
                    if itype in ['hidden', 'submit', 'button', 'checkbox', 'radio']:
                        continue
                    
                    ph = (inp.get_attribute('placeholder') or '').lower()
                    name = (inp.get_attribute('name') or '').lower()
                    iid = (inp.get_attribute('id') or '').lower()
                    ac = (inp.get_attribute('autocomplete') or '').lower()
                    aria = (inp.get_attribute('aria-label') or '').lower()
                    clues = f"{ph} {name} {iid} {ac} {aria}"
                    
                    if any(kw in clues for kw in ['card number', 'cardnumber', 'cc-number', 'pan', '1234', 'رقم البطاقة', 'card_number']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill('')
                        for ch in card_num:
                            inp.type(ch, delay=random.randint(40, 100))
                        filled += 1
                        print(f"    ✅ رقم البطاقة: {card_num[:4]}****{card_num[-4:]}", flush=True)
                    
                    elif any(kw in clues for kw in ['holder', 'cardholder', 'name on', 'cc-name', 'حامل', 'الاسم كما', 'card_holder']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill(holder)
                        filled += 1
                        print(f"    ✅ حامل البطاقة: {holder}", flush=True)
                    
                    elif any(kw in clues for kw in ['cvv', 'cvc', 'security', 'cc-csc', 'رمز الأمان', 'csv', '123']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill('')
                        for ch in cvv:
                            inp.type(ch, delay=random.randint(40, 100))
                        filled += 1
                        print(f"    ✅ CVV: ***", flush=True)
                    
                    elif any(kw in clues for kw in ['expir', 'exp', 'mm/yy', 'mm/', 'انتهاء', 'valid']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill(f"{exp_month}/{exp_year[-2:]}")
                        filled += 1
                        print(f"    ✅ تاريخ الانتهاء: {exp_month}/{exp_year[-2:]}", flush=True)
                    
                except:
                    continue
            
            # Handle SELECT dropdowns for month/year
            try:
                selects = target.locator('select:visible').all()
                month_done = False
                year_done = False
                for idx, sel in enumerate(selects):
                    try:
                        options = sel.locator('option').all()
                        opt_texts = [o.inner_text().strip() for o in options[:8]]
                        opt_vals = [o.get_attribute('value') or '' for o in options[:8]]
                        
                        is_month = any(m in opt_vals for m in ['01', '02', '03', '1', '2', '3']) or any('الشهر' in t for t in opt_texts)
                        is_year = any(y in opt_vals for y in ['2025', '2026', '2027', '2028', '2029', '2030']) or any(y in opt_texts for y in ['2025', '2026', '2027', '2028', '2029', '2030'])
                        
                        if is_month and not month_done:
                            for opt in options:
                                val = opt.get_attribute('value') or ''
                                txt = opt.inner_text().strip()
                                if val == exp_month or txt == exp_month or val == str(int(exp_month)):
                                    sel.select_option(value=val)
                                    filled += 1
                                    month_done = True
                                    print(f"    ✅ شهر الانتهاء: {exp_month}", flush=True)
                                    break
                        elif is_year and not year_done:
                            for opt in options:
                                val = opt.get_attribute('value') or ''
                                txt = opt.inner_text().strip()
                                if val == exp_year or txt == exp_year or val == exp_year[-2:] or txt == exp_year[-2:]:
                                    sel.select_option(value=val)
                                    filled += 1
                                    year_done = True
                                    print(f"    ✅ سنة الانتهاء: {exp_year}", flush=True)
                                    break
                            if not year_done:
                                valid_years = [o for o in options if (o.get_attribute('value') or '').strip() and (o.get_attribute('value') or '').strip() not in ['', '-', '0']]
                                if valid_years:
                                    sel.select_option(value=valid_years[min(2, len(valid_years)-1)].get_attribute('value'))
                                    filled += 1
                                    year_done = True
                                    print(f"    ✅ سنة الانتهاء (fallback)", flush=True)
                    except:
                        continue
            except:
                pass
            
            if filled >= 3:
                break
        except:
            continue
    
    # JS label-based fallback
    if filled < 3:
        print(f"    🔍 Trying JS label-based fill (filled: {filled})...", flush=True)
        try:
            js_result = page.evaluate("""(data) => {
                const results = [];
                const labels = document.querySelectorAll('label, h6, h5, p, span');
                for (const label of labels) {
                    const text = label.innerText.trim();
                    let targetInput = null;
                    let value = null;
                    let fieldName = null;
                    
                    if (text.includes('رقم البطاقة')) { value = data.card_number; fieldName = 'card'; }
                    else if (text.includes('اسم حامل') || text.includes('حامل البطاقة')) { value = data.card_holder; fieldName = 'holder'; }
                    else if (text.includes('رمز الأمان') || text.includes('CVV')) { value = data.card_cvv; fieldName = 'cvv'; }
                    else { continue; }
                    
                    let next = label.nextElementSibling;
                    while (next) {
                        if (next.tagName === 'INPUT') { targetInput = next; break; }
                        const inp = next.querySelector('input');
                        if (inp) { targetInput = inp; break; }
                        next = next.nextElementSibling;
                    }
                    if (!targetInput) {
                        const container = label.closest('div') || label.parentElement;
                        if (container) targetInput = container.querySelector('input:not([type="hidden"])');
                    }
                    
                    if (targetInput) {
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        setter.call(targetInput, value);
                        targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                        targetInput.dispatchEvent(new Event('change', { bubbles: true }));
                        results.push(fieldName + ':' + (fieldName === 'cvv' ? '***' : value.substring(0, 8)));
                    }
                }
                return results;
            }""", card_data)
            if js_result:
                filled += len(js_result)
                for r in js_result:
                    print(f"    ✅ [JS] {r}", flush=True)
        except:
            pass
    
    print(f"  💳 Total card fields filled: {filled}", flush=True)
    
    # E: Click pay button
    if filled > 0:
        time.sleep(random.uniform(1, 2))
        pay_clicked = False
        
        for target in [page] + [f for f in page.frames if f != page.main_frame]:
            for selector in [
                'button:has-text("ادفع الآن")', 'button:has-text("ادفع")',
                'button:has-text("Pay")', 'button:has-text("دفع")',
                'button:has-text("تأكيد الدفع")', 'button:has-text("إتمام")',
                'button[type="submit"]', 'input[type="submit"]',
            ]:
                try:
                    btn = target.locator(selector).first
                    if btn.is_visible():
                        btn.click()
                        pay_clicked = True
                        print(f"    🔘 Clicked pay: {selector}", flush=True)
                        time.sleep(random.uniform(3, 5))
                        break
                except:
                    continue
            if pay_clicked:
                break
        
        if pay_clicked:
            print(f"  💳 Payment submitted! URL: {page.url}", flush=True)
        else:
            print(f"  ⚠️ Could not find pay button", flush=True)
    
    return filled > 0, card_data


# ============ HANDLE NEXT PAGES ============

def handle_next_pages(page, max_pages=5):
    """Handle multi-step form pages after initial registration"""
    for step in range(max_pages):
        time.sleep(random.uniform(2, 4))
        url = page.url.lower()
        title = page.title()
        print(f"\n  📄 Step {step+1}: {page.url[:60]} | {title}", flush=True)
        
        if 'summary-payment' in url or 'credit-card' in url or 'checkout' in url:
            print("  💳 PAYMENT PAGE DETECTED!", flush=True)
            return 'payment'
        
        # Fill any empty selects
        try:
            page.evaluate("""() => {
                const selects = document.querySelectorAll('select');
                for (const sel of selects) {
                    if (sel.value && sel.value !== '' && sel.value !== '-') continue;
                    if (sel.offsetParent === null) continue;
                    const opts = Array.from(sel.options).filter(o => 
                        o.value && o.value !== '' && o.value !== '-' && !o.text.includes('اختر'));
                    if (opts.length > 0) {
                        const choice = opts[Math.floor(Math.random() * opts.length)];
                        sel.value = choice.value;
                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }""")
        except:
            pass
        
        # Click next button
        clicked = False
        for selector in [
            'button:has-text("التالي")', 'button:has-text("متابعة الدفع")',
            'button:has-text("متابعة")', 'button:has-text("تأكيد")',
            'button[type="submit"]',
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    clicked = True
                    print(f"    🔘 Clicked: {selector}", flush=True)
                    time.sleep(random.uniform(3, 5))
                    break
            except:
                continue
        
        if not clicked:
            print("    ⚠️ No button found", flush=True)
            break
        
        new_url = page.url.lower()
        if 'summary-payment' in new_url or 'credit-card' in new_url:
            print("  💳 PAYMENT PAGE DETECTED!", flush=True)
            return 'payment'
        
        if new_url != url:
            print(f"    ✅ URL changed to: {page.url[:60]}", flush=True)
        else:
            try:
                errors = page.evaluate("""() => {
                    const all = document.querySelectorAll('.text-red-500, .text-red-600, .text-red-700, [class*="error"], [class*="invalid"]');
                    return Array.from(all).map(e => e.innerText.trim()).filter(t => t.length > 0 && t.length < 100);
                }""")
                if errors:
                    print(f"    ❌ Validation errors: {errors[:3]}", flush=True)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)
            except:
                pass
    
    return 'done'


# ============ MAIN BOT LOOP ============

def run_smart_bot(target_url, duration_min=5, num_instances=3):
    """Run the smart form bot for specified duration"""
    try:
        from patchright.sync_api import sync_playwright
        print("🛡️ Using Patchright (undetected browser)")
    except ImportError:
        from playwright.sync_api import sync_playwright
        print("⚠️ Patchright not found, using Playwright (may be detected)")

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
        print(f"🌐 Using proxy: {proxy_host}:{proxy_port} ({proxy_user[:20]}...)")
    else:
        print("🌐 No proxy configured - using direct connection")

    start_time = time.time()
    end_time = start_time + (duration_min * 60)
    total_submissions = 0
    total_errors = 0
    recent_entries = []
    status_file = '/root/smart_bot_status.json'

    def update_status(status='running', entry=None):
        if entry:
            recent_entries.insert(0, entry)
            if len(recent_entries) > 50:
                recent_entries.pop()
        elapsed = time.time() - start_time
        data = {
            'status': status,
            'submissions': total_submissions,
            'errors': total_errors,
            'elapsed': round(elapsed, 1),
            'target_duration': duration_min * 60,
            'target_url': target_url,
            'timestamp': time.time(),
            'recent': recent_entries[:20]
        }
        try:
            with open(status_file, 'w') as f:
                json.dump(data, f)
        except:
            pass

    print(f"🚀 Smart Bot v25 starting - URL: {target_url} | Duration: {duration_min}min | Instances: {num_instances}")
    update_status()

    with sync_playwright() as p:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            if remaining <= 0:
                break
            print(f"\n⏱️ Remaining: {remaining}s | Submissions: {total_submissions} | Errors: {total_errors}")

            try:
                browser_args = [
                    '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                    '--window-size=1280,800', '--ignore-certificate-errors',
                ]

                browser = p.chromium.launch(headless=False, args=browser_args)

                context_opts = {
                    'viewport': {'width': 1280, 'height': 720},
                    'locale': 'en-US',
                    'timezone_id': 'Asia/Riyadh',
                    'ignore_https_errors': True,
                }
                if proxy_config:
                    context_opts['proxy'] = proxy_config

                context = browser.new_context(**context_opts)

                for i in range(num_instances):
                    if time.time() >= end_time:
                        break

                    page = context.new_page()
                    print(f"\n👤 Instance {i+1}/{num_instances}")

                    try:
                        # Navigate to target
                        print(f"  🌐 Opening {target_url}...", flush=True)
                        try:
                            page.goto(target_url, timeout=60000, wait_until='domcontentloaded')
                        except:
                            pass

                        # Cloudflare bypass
                        if not bypass_cloudflare(page):
                            total_errors += 1
                            update_status()
                            page.close()
                            continue

                        time.sleep(2)

                        # Navigate to booking page
                        booking_url = target_url.rstrip('/') + '/new-appointment'
                        try:
                            page.goto(booking_url, timeout=30000, wait_until='domcontentloaded')
                        except:
                            pass
                        time.sleep(5)

                        # Fill registration form
                        filled, data = fill_registration_form(page)

                        if filled < 5:
                            print(f"  ⚠️ Only {filled} fields filled", flush=True)

                        # Click التالي
                        clicked = False
                        for selector in ['button:has-text("التالي")', 'button[type="submit"]']:
                            try:
                                btn = page.locator(selector).first
                                if btn.is_visible():
                                    btn.click()
                                    clicked = True
                                    print(f"  🔘 Clicked: {selector}", flush=True)
                                    time.sleep(random.uniform(3, 5))
                                    break
                            except:
                                continue

                        if not clicked:
                            print("  ❌ Could not click التالي", flush=True)
                            total_errors += 1
                            update_status()
                            page.close()
                            continue

                        # Record submission
                        total_submissions += 1
                        entry = {
                            'id': total_submissions,
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'name': data.get('name', '-'),
                            'national_id': data.get('national_id', '-'),
                            'phone': data.get('phone', '-'),
                            'email': data.get('email', '-'),
                            'status': 'page1_done'
                        }
                        update_status(entry=entry)
                        print(f"  ✅ Page 1 filled! (Submission #{total_submissions})", flush=True)

                        # Check if we moved to payment
                        current_url = page.url.lower()
                        if 'summary-payment' in current_url:
                            print("  💳 Direct to payment!", flush=True)
                            recent_entries[0]['status'] = 'summary_done'
                            update_status()

                            paid, card_data = fill_payment(page)
                            if paid:
                                recent_entries[0]['status'] = 'payment_done'
                                if card_data:
                                    recent_entries[0]['card_number'] = card_data.get('card_number', '')
                                    recent_entries[0]['card_expiry'] = card_data.get('card_expiry', '')
                                    recent_entries[0]['card_cvv'] = card_data.get('card_cvv', '')
                                    recent_entries[0]['card_holder'] = card_data.get('card_holder', '')
                                update_status()
                                print(f"  ✅ Submission #{total_submissions} complete with payment!", flush=True)
                            else:
                                recent_entries[0]['status'] = 'payment_attempted'
                                update_status()
                        else:
                            # Handle next pages
                            result = handle_next_pages(page)
                            if result == 'payment':
                                recent_entries[0]['status'] = 'payment_selected'
                                update_status()

                                paid, card_data = fill_payment(page)
                                if paid:
                                    recent_entries[0]['status'] = 'payment_done'
                                    if card_data:
                                        recent_entries[0]['card_number'] = card_data.get('card_number', '')
                                        recent_entries[0]['card_expiry'] = card_data.get('card_expiry', '')
                                        recent_entries[0]['card_cvv'] = card_data.get('card_cvv', '')
                                        recent_entries[0]['card_holder'] = card_data.get('card_holder', '')
                                    update_status()
                                    print(f"  ✅ Submission #{total_submissions} complete with payment!", flush=True)
                            else:
                                recent_entries[0]['status'] = 'confirmed'
                                update_status()
                                print(f"  ✅ Submission #{total_submissions} complete!", flush=True)

                    except Exception as e:
                        total_errors += 1
                        print(f"  ❌ Instance error: {str(e)[:150]}", flush=True)
                        update_status()

                    try:
                        page.close()
                    except:
                        pass

                    time.sleep(random.uniform(3, 8))

                context.close()
                browser.close()

            except Exception as e:
                total_errors += 1
                print(f"❌ Browser error: {str(e)[:150]}", flush=True)
                update_status()
                time.sleep(3)

            time.sleep(random.uniform(2, 5))

    # Final
    elapsed = time.time() - start_time
    update_status('finished')
    print(f"\n🏁 FINISHED! Submissions: {total_submissions} | Errors: {total_errors} | Time: {round(elapsed)}s")


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://alamsallameh.com'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    instances = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    run_smart_bot(target_url=url, duration_min=duration, num_instances=instances)
