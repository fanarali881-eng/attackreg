#!/usr/bin/env python3
"""
Smart Universal Form Bot v22 - Detects and fills ANY booking/registration form
Uses Playwright (real Chrome browser) + intelligent form detection
Generates random Saudi data for all field types
FIXES: Better page navigation, smarter payment detection, proxy retry logic
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
    """Generate a valid Iqama number (starts with 2) that passes checksum validation"""
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

# Real Saudi bank BIN numbers (first 6 digits) mapped to bank names
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

def gen_card_number():
    """Generate a fake card number using real Saudi bank BINs + Luhn algorithm"""
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
    return ''.join(str(d) for d in digits)

def gen_card_number_with_bank():
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
    month = random.randint(1, 12)
    year = random.randint(27, 30)
    return f"{month:02d}/{year}"

def gen_card_expiry_month():
    return f"{random.randint(1, 12):02d}"

def gen_card_expiry_year():
    return str(random.randint(2027, 2030))

def gen_cvv():
    return str(random.randint(100, 999))

def gen_cardholder_name():
    first_en = random.choice(['Mohammed', 'Abdullah', 'Fahad', 'Saud', 'Khalid', 'Sultan', 'Turki', 'Bandar', 'Faisal', 'Ahmad', 'Omar', 'Youssef', 'Ibrahim', 'Nasser', 'Saad'])
    last_en = random.choice(['Alotaibi', 'Alharbi', 'Alqahtani', 'Alshamri', 'Aldosari', 'Almutairi', 'Alghamdi', 'Alzahrani', 'Alsubaie', 'Alshehri', 'Aljohani', 'Alanazi', 'Alrashidi'])
    return f"{first_en} {last_en}"

def gen_number_string(length=4):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


# ============ SMART FIELD DETECTION ============

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
        'keywords': ['مدينة', 'المدينة', 'city', 'town'],
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
    'card_number': {
        'keywords': ['رقم البطاقة', 'card number', 'رقم الكرت', 'card no', 'credit card', 'debit card', 'visa', 'mada', 'ماستركارد', 'فيزا', 'مدى', 'pan'],
        'generator': gen_card_number
    },
    'card_expiry': {
        'keywords': ['تاريخ الانتهاء', 'expiry', 'expiration', 'exp date', 'انتهاء', 'صلاحية', 'mm/yy', 'valid thru', 'valid until'],
        'generator': gen_card_expiry
    },
    'card_expiry_month': {
        'keywords': ['expiry month', 'exp month', 'شهر الانتهاء', 'mm'],
        'generator': gen_card_expiry_month
    },
    'card_expiry_year': {
        'keywords': ['expiry year', 'exp year', 'سنة الانتهاء', 'yy', 'yyyy'],
        'generator': gen_card_expiry_year
    },
    'cvv': {
        'keywords': ['cvv', 'cvc', 'cvv2', 'cvc2', 'security code', 'رمز الأمان', 'رمز التحقق', 'الرمز السري', 'csv'],
        'generator': gen_cvv
    },
    'cardholder_name': {
        'keywords': ['cardholder', 'card holder', 'اسم حامل البطاقة', 'name on card', 'اسم على البطاقة', 'holder name'],
        'generator': gen_cardholder_name
    },
}


def detect_field_type(element_info):
    """Detect what type of data a form field expects based on its attributes"""
    clues = ' '.join([
        element_info.get('placeholder', ''),
        element_info.get('label', ''),
        element_info.get('name', ''),
        element_info.get('id', ''),
        element_info.get('aria_label', ''),
        element_info.get('nearby_text', ''),
    ]).lower()

    input_type = element_info.get('type', 'text').lower()
    if input_type == 'email':
        return 'email'
    if input_type == 'tel':
        return 'phone'
    if input_type == 'date':
        return 'date'
    if input_type == 'number':
        for field_type, patterns in FIELD_PATTERNS.items():
            for kw in patterns['keywords']:
                if kw in clues:
                    return field_type
        return 'generic_number'

    best_match = None
    best_score = 0
    for field_type, patterns in FIELD_PATTERNS.items():
        for kw in patterns['keywords']:
            if kw in clues:
                score = len(kw)
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
        return random.choice([gen_name(), gen_city(), gen_address()])
    return ''


# ============ SMART PAGE ANALYSIS ============

def analyze_page_content(page, log_fn=print):
    """
    Analyze the current page to determine what type it is:
    - 'form': Has form fields to fill
    - 'payment': Has payment-specific fields (card number inputs, payment iframes)
    - 'summary': Has summary/confirmation content with action buttons
    - 'success': Booking confirmed / success page
    - 'error': Error page or geo-blocked
    - 'unknown': Can't determine
    """
    try:
        page_text = page.inner_text('body').lower()
    except:
        return 'unknown', {}
    
    info = {
        'visible_inputs': 0,
        'visible_selects': 0,
        'has_card_fields': False,
        'has_payment_iframe': False,
        'has_form_fields': False,
        'page_text_snippet': page_text[:500],
    }
    
    # Count visible form elements
    try:
        info['visible_inputs'] = page.locator('input:visible').count()
        info['visible_selects'] = page.locator('select:visible').count()
    except:
        pass
    
    # Check for geo-blocking
    geo_block_keywords = ['غير متاح', 'not available', 'غير متاحة', 'blocked', 'restricted']
    if any(kw in page_text for kw in geo_block_keywords):
        log_fn("🚫 Page appears geo-blocked!")
        return 'error', info
    
    # Check for success/confirmation
    success_keywords = ['تم الحجز', 'تم بنجاح', 'successfully', 'booking confirmed', 'تأكيد الحجز',
                       'شكراً', 'thank you', 'تم التسجيل', 'registration complete', 'رقم الحجز',
                       'booking number', 'reference number', 'رقم المرجع']
    if any(kw in page_text for kw in success_keywords):
        log_fn("🎉 Success/confirmation page detected!")
        return 'success', info
    
    # Check for ACTUAL payment fields (not just payment-related words in footer)
    # Look for card number input fields specifically
    try:
        card_input_clues = ['card', 'cardnumber', 'cc-number', 'pan', 'رقم البطاقة', 'رقم الكرت']
        all_inputs = page.locator('input:visible').all()
        for inp in all_inputs:
            try:
                inp_clues = ' '.join([
                    (inp.get_attribute('placeholder') or ''),
                    (inp.get_attribute('name') or ''),
                    (inp.get_attribute('id') or ''),
                    (inp.get_attribute('autocomplete') or ''),
                    (inp.get_attribute('aria-label') or ''),
                ]).lower()
                if any(kw in inp_clues for kw in card_input_clues):
                    info['has_card_fields'] = True
                    break
            except:
                continue
    except:
        pass
    
    # Check for payment iframes (many payment gateways use iframes)
    try:
        frames = page.frames
        for frame in frames:
            if frame == page.main_frame:
                continue
            try:
                frame_url = frame.url.lower()
                if any(kw in frame_url for kw in ['payment', 'pay', 'checkout', 'card', 'stripe', 'payfort', 'hyperpay', 'moyasar']):
                    info['has_payment_iframe'] = True
                    break
                # Check if iframe has card inputs
                frame_inputs = frame.locator('input:visible').count()
                if frame_inputs > 0:
                    for inp in frame.locator('input:visible').all():
                        try:
                            inp_clues = ' '.join([
                                (inp.get_attribute('placeholder') or ''),
                                (inp.get_attribute('name') or ''),
                                (inp.get_attribute('id') or ''),
                            ]).lower()
                            if any(kw in inp_clues for kw in card_input_clues):
                                info['has_payment_iframe'] = True
                                break
                        except:
                            continue
            except:
                continue
    except:
        pass
    
    # If actual card fields found, it's a payment page
    if info['has_card_fields'] or info['has_payment_iframe']:
        log_fn("💳 Real payment page detected (has card input fields)")
        return 'payment', info
    
    # Check for regular form fields (inputs that are NOT card-related)
    regular_input_count = 0
    try:
        for inp in page.locator('input:visible').all():
            try:
                inp_type = (inp.get_attribute('type') or 'text').lower()
                if inp_type not in ['hidden', 'submit', 'button', 'image', 'file']:
                    regular_input_count += 1
            except:
                continue
    except:
        pass
    
    info['has_form_fields'] = regular_input_count > 0 or info['visible_selects'] > 0
    
    if info['has_form_fields']:
        log_fn(f"📋 Form page detected ({regular_input_count} inputs, {info['visible_selects']} selects)")
        return 'form', info
    
    # Check for summary/confirmation page with action buttons
    summary_keywords = ['ملخص', 'summary', 'تأكيد', 'confirm', 'مراجعة', 'review',
                       'التفاصيل', 'details', 'المبلغ', 'amount', 'الإجمالي', 'total',
                       'المقابل المالي']
    has_action_buttons = False
    try:
        buttons = page.locator('button:visible, a.btn:visible, input[type="submit"]:visible').all()
        action_keywords = ['التالي', 'تأكيد', 'إتمام', 'دفع', 'ادفع', 'next', 'confirm', 'pay',
                          'proceed', 'continue', 'متابعة', 'موافق', 'تأكيد الحجز', 'إتمام الحجز']
        for btn in buttons:
            try:
                btn_text = btn.inner_text().strip().lower()
                if any(kw in btn_text for kw in action_keywords):
                    has_action_buttons = True
                    break
            except:
                continue
    except:
        pass
    
    if has_action_buttons:
        log_fn("📄 Summary/action page detected")
        return 'summary', info
    
    return 'unknown', info


# ============ PLAYWRIGHT SMART FORM FILLER ============

def fill_form_on_page(page, log_fn=print):
    """
    Fill all form fields on the CURRENT page (without navigating to a new URL).
    Returns: (filled_data dict, filled_count, submitted bool)
    """
    filled_count = 0
    selected_count = 0
    clicked_count = 0
    filled_data = {}

    # ===== STEP 1: Detect and fill text inputs =====
    log_fn("🔍 Scanning form fields...")

    inputs = page.locator('input:visible').all()
    for inp in inputs:
        try:
            input_type = (inp.get_attribute('type') or 'text').lower()
            if input_type in ['hidden', 'submit', 'button', 'image', 'file', 'checkbox', 'radio']:
                continue

            element_info = {
                'type': input_type,
                'placeholder': inp.get_attribute('placeholder') or '',
                'name': inp.get_attribute('name') or '',
                'id': inp.get_attribute('id') or '',
                'aria_label': inp.get_attribute('aria-label') or '',
                'label': '',
                'nearby_text': '',
            }

            field_id = inp.get_attribute('id')
            if field_id:
                try:
                    label = page.locator(f'label[for="{field_id}"]')
                    if label.count() > 0:
                        element_info['label'] = label.first.inner_text()
                except:
                    pass

            try:
                parent_text = inp.evaluate('el => el.parentElement ? el.parentElement.innerText : ""')
                element_info['nearby_text'] = parent_text[:200] if parent_text else ''
            except:
                pass

            field_type = detect_field_type(element_info)
            value = generate_value_for_field(field_type)

            if value:
                inp.click()
                time.sleep(random.uniform(0.2, 0.5))
                inp.fill('')
                time.sleep(random.uniform(0.1, 0.3))

                if input_type == 'date':
                    inp.fill(value)
                else:
                    if len(value) <= 20:
                        for char in value:
                            inp.type(char, delay=random.randint(30, 100))
                    else:
                        inp.fill(value)

                filled_count += 1
                filled_data[field_type] = value
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

    # ===== STEP 3: Handle select dropdowns (SMART - 3 passes for dependent selects) =====
    for select_pass in range(3):
        selects = page.locator('select:visible').all()
        for sel in selects:
            try:
                sel_name = (sel.get_attribute('name') or '').lower()
                sel_id = (sel.get_attribute('id') or '').lower()
                sel_label = ''
                try:
                    sid = sel.get_attribute('id')
                    if sid:
                        lbl = page.locator(f'label[for="{sid}"]')
                        if lbl.count() > 0:
                            sel_label = lbl.first.inner_text().lower()
                except:
                    pass
                try:
                    parent_text = sel.evaluate('el => el.parentElement ? el.parentElement.innerText : ""')
                    sel_nearby = (parent_text or '').lower()[:200]
                except:
                    sel_nearby = ''
                
                sel_clues = f"{sel_name} {sel_id} {sel_label} {sel_nearby}"
                
                options = sel.locator('option').all()
                if len(options) <= 1:
                    continue
                
                try:
                    current_val = sel.input_value()
                    if current_val and current_val != '' and select_pass > 0:
                        continue
                except:
                    pass
                
                start_idx = 0
                try:
                    first_text = options[0].inner_text().strip()
                    if any(kw in first_text.lower() for kw in ['اختر', 'اختار', 'select', '--', '- -', 'choose', 'الكل', 'حدد']):
                        start_idx = 1
                except:
                    start_idx = 1
                
                if start_idx >= len(options):
                    continue
                
                chosen_idx = None
                
                # Nationality/country dropdown - ALWAYS choose Saudi
                is_nationality = any(kw in sel_clues for kw in ['جنسية', 'nationality', 'الجنسية', 'بلد', 'country', 'دولة'])
                if is_nationality:
                    for i in range(start_idx, len(options)):
                        try:
                            opt_text = options[i].inner_text().strip()
                            if any(kw in opt_text for kw in ['السعودية', 'سعودي', 'Saudi', 'saudi', 'المملكة']):
                                chosen_idx = i
                                break
                        except:
                            continue
                
                # Vehicle status
                is_vehicle_status = any(kw in sel_clues for kw in ['حالة المركبة', 'vehicle status', 'رخصة سير'])
                if is_vehicle_status:
                    for i in range(start_idx, len(options)):
                        try:
                            opt_text = options[i].inner_text().strip()
                            if 'رخصة' in opt_text or 'تحمل' in opt_text:
                                chosen_idx = i
                                break
                        except:
                            continue
                
                if chosen_idx is None:
                    chosen_idx = random.randint(start_idx, len(options) - 1)
                
                sel.select_option(index=chosen_idx)
                selected_count += 1
                try:
                    selected_text = options[chosen_idx].inner_text().strip()
                    log_fn(f"  ✅ [select] = {selected_text[:30]}")
                    filled_data[f'select_{sel_name or sel_id or str(selected_count)}'] = selected_text
                except:
                    log_fn(f"  ✅ [select] index={chosen_idx}")
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                log_fn(f"  ⚠️ Skip select: {str(e)[:50]}")
                continue
        
        if select_pass < 2:
            time.sleep(random.uniform(1, 2))

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

    # ===== STEP 5: Handle checkboxes =====
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

    # ===== STEP 5.5: Handle selection/toggle buttons =====
    selection_keywords = [
        'تحمل رخصة سير', 'تحمل بطاقة جمركية', 'رخصة سير', 'بطاقة جمركية',
        'نعم', 'لا', 'ذكر', 'أنثى', 'فرد', 'شركة', 'مؤسسة',
        'شخصي', 'تجاري', 'حكومي', 'عسكري',
    ]
    
    skip_keywords = ['التالي', 'تالي', 'إرسال', 'ارسال', 'حجز', 'تأكيد', 'submit', 'next', 'إتمام', 'تسجيل']
    
    all_buttons = page.locator('button:visible, [role="button"]:visible, .btn:visible, [class*="option"]:visible, [class*="select"]:visible, [class*="choice"]:visible, [class*="toggle"]:visible').all()
    for btn in all_buttons:
        try:
            btn_text = btn.inner_text().strip()
            if not btn_text:
                continue
            if any(sk in btn_text.lower() for sk in skip_keywords):
                continue
            for kw in selection_keywords:
                if kw in btn_text:
                    if 'رخصة سير' in btn_text or 'نعم' in btn_text or 'ذكر' in btn_text or 'فرد' in btn_text or 'شخصي' in btn_text:
                        btn.click()
                        clicked_count += 1
                        log_fn(f"  ✅ [selection_btn] = {btn_text}")
                        time.sleep(random.uniform(0.5, 1))
                        break
        except:
            continue
    
    # Also try clicking div/span that looks like selection option
    try:
        option_elements = page.locator('[class*="card"]:visible, [class*="option"]:visible, [class*="item"]:visible').all()
        for el in option_elements:
            try:
                el_text = el.inner_text().strip()
                if 'رخصة سير' in el_text:
                    el.click()
                    clicked_count += 1
                    log_fn(f"  ✅ [selection_card] = {el_text[:40]}")
                    time.sleep(random.uniform(0.5, 1))
                    break
            except:
                continue
    except:
        pass

    log_fn(f"📊 Filled: {filled_count} inputs | {selected_count} selects | {clicked_count} clicks")
    
    return filled_data, filled_count + selected_count + clicked_count


def click_submit_button(page, log_fn=print):
    """Find and click the submit/next button on the current page. Returns True if clicked."""
    time.sleep(random.uniform(1, 2))

    submit_keywords = [
        'التالي', 'تالي', 'إرسال', 'ارسال', 'حجز', 'تأكيد', 'تسجيل', 'إتمام', 'اتمام',
        'submit', 'next', 'book', 'confirm', 'register', 'send', 'continue',
        'حفظ', 'save', 'تقديم', 'موافق', 'ok', 'proceed', 'احجز', 'سجل',
        'ابدأ', 'بدء', 'start', 'go', 'متابعة'
    ]

    # Try buttons first
    buttons = page.locator('button:visible').all()
    for btn in buttons:
        try:
            btn_text = btn.inner_text().strip().lower()
            btn_type = (btn.get_attribute('type') or '').lower()

            if any(skip in btn_text for skip in ['إلغاء', 'cancel', 'رجوع', 'back', 'مسح', 'clear']):
                continue

            for kw in submit_keywords:
                if kw in btn_text or btn_type == 'submit':
                    log_fn(f"🖱️ Clicking button: '{btn_text[:30]}'")
                    btn.click()
                    return True
        except:
            continue

    # Try input[type=submit]
    try:
        submit_input = page.locator('input[type="submit"]:visible').first
        if submit_input:
            log_fn(f"🖱️ Clicking submit input")
            submit_input.click()
            return True
    except:
        pass

    # Try links that look like buttons
    try:
        links = page.locator('a:visible').all()
        for link in links:
            try:
                link_text = link.inner_text().strip().lower()
                for kw in submit_keywords:
                    if kw in link_text:
                        log_fn(f"🖱️ Clicking link: '{link_text[:30]}'")
                        link.click()
                        return True
            except:
                continue
    except:
        pass

    log_fn("⚠️ No submit button found")
    return False


def click_action_button(page, log_fn=print):
    """Click action/confirm/pay button on summary pages. Returns True if clicked."""
    action_keywords = ['التالي', 'تأكيد', 'إتمام', 'دفع', 'ادفع', 'next', 'confirm', 'pay',
                      'proceed', 'continue', 'متابعة', 'موافق', 'تأكيد الحجز', 'إتمام الحجز',
                      'الدفع', 'ادفع الآن', 'pay now', 'complete', 'إكمال']
    
    buttons = page.locator('button:visible, a:visible, input[type="submit"]:visible').all()
    for btn in buttons:
        try:
            btn_text = btn.inner_text().strip().lower()
            if any(skip in btn_text for skip in ['إلغاء', 'cancel', 'رجوع', 'back']):
                continue
            for kw in action_keywords:
                if kw in btn_text:
                    log_fn(f"🔘 Clicking action: '{btn_text[:30]}'")
                    btn.click()
                    return True
        except:
            continue
    
    log_fn("⚠️ No action button found on summary page")
    return False


def handle_payment_page(page, log_fn=print):
    """Handle payment page - click payment method, fill card details, submit."""
    try:
        log_fn("💳 Handling payment...")
        time.sleep(random.uniform(2, 3))

        # Try to click payment method button (Visa, Mada, etc)
        payment_method_keywords = ['visa', 'فيزا', 'mada', 'مدى', 'بطاقة ائتمان', 'credit card',
                                   'بطاقة مدى', 'mastercard', 'ماستركارد', 'ادفع', 'pay now',
                                   'الدفع بالبطاقة', 'card payment']

        buttons = page.locator('button:visible, a:visible, div[role="button"]:visible, input[type="radio"]:visible, label:visible').all()
        for btn in buttons:
            try:
                btn_text = btn.inner_text().strip().lower()
                for kw in payment_method_keywords:
                    if kw in btn_text:
                        log_fn(f"💳 Clicking payment method: '{btn_text[:30]}'")
                        btn.click()
                        time.sleep(random.uniform(2, 4))
                        break
            except:
                continue

        # Also try clicking payment logo images
        try:
            imgs = page.locator('img:visible').all()
            for img in imgs:
                alt = (img.get_attribute('alt') or '').lower()
                src = (img.get_attribute('src') or '').lower()
                if any(kw in alt + src for kw in ['visa', 'mada', 'mastercard', 'credit']):
                    log_fn(f"💳 Clicking payment logo: {alt or src[:30]}")
                    img.click()
                    time.sleep(random.uniform(2, 3))
                    break
        except:
            pass

        # Fill card details - check main page first, then iframes
        card_filled = fill_card_fields(page, log_fn)

        if not card_filled:
            log_fn("🔍 Checking iframes for payment form...")
            frames = page.frames
            for frame in frames:
                if frame == page.main_frame:
                    continue
                try:
                    frame_inputs = frame.locator('input:visible').count()
                    if frame_inputs > 0:
                        log_fn(f"📋 Found iframe with {frame_inputs} inputs")
                        card_filled = fill_card_fields_in_frame(frame, log_fn)
                        if card_filled:
                            break
                except:
                    continue

        # Click pay/submit button
        if card_filled:
            time.sleep(random.uniform(1, 2))
            pay_keywords = ['ادفع', 'pay', 'دفع', 'تأكيد الدفع', 'confirm payment', 'submit',
                           'إرسال', 'تأكيد', 'confirm', 'إتمام الدفع', 'complete payment',
                           'pay now', 'ادفع الآن', 'proceed']

            all_clickable = page.locator('button:visible, input[type="submit"]:visible, a:visible').all()
            for elem in all_clickable:
                try:
                    elem_text = elem.inner_text().strip().lower()
                    elem_value = (elem.get_attribute('value') or '').lower()
                    combined = elem_text + ' ' + elem_value
                    for kw in pay_keywords:
                        if kw in combined:
                            log_fn(f"💳 Clicking pay button: '{elem_text[:30]}'")
                            elem.click()
                            time.sleep(random.uniform(3, 5))
                            try:
                                page.wait_for_load_state('networkidle', timeout=10000)
                            except:
                                pass
                            log_fn(f"💳 Payment submitted! URL: {page.url}")
                            return True
                except:
                    continue

            # Check inside iframes for pay button
            for frame in page.frames:
                if frame == page.main_frame:
                    continue
                try:
                    frame_buttons = frame.locator('button:visible, input[type="submit"]:visible').all()
                    for btn in frame_buttons:
                        try:
                            btn_text = btn.inner_text().strip().lower()
                            btn_value = (btn.get_attribute('value') or '').lower()
                            combined = btn_text + ' ' + btn_value
                            for kw in pay_keywords:
                                if kw in combined:
                                    log_fn(f"💳 Clicking pay button in iframe: '{btn_text[:30]}'")
                                    btn.click()
                                    time.sleep(random.uniform(3, 5))
                                    return True
                        except:
                            continue
                except:
                    continue

        log_fn("⚠️ Payment handling attempted" + (" (card filled)" if card_filled else " (no card fields found)"))
        return card_filled

    except Exception as e:
        log_fn(f"❌ Payment error: {str(e)}")
        return False


def fill_card_fields(page, log_fn=print):
    """Fill credit card fields on the main page"""
    card_num = gen_card_number()
    expiry = gen_card_expiry()
    cvv = gen_cvv()
    holder = gen_cardholder_name()
    filled = 0

    inputs = page.locator('input:visible').all()
    for inp in inputs:
        try:
            input_type = (inp.get_attribute('type') or 'text').lower()
            if input_type in ['hidden', 'submit', 'button', 'checkbox', 'radio']:
                continue

            clues = ' '.join([
                (inp.get_attribute('placeholder') or ''),
                (inp.get_attribute('name') or ''),
                (inp.get_attribute('id') or ''),
                (inp.get_attribute('aria-label') or ''),
                (inp.get_attribute('autocomplete') or ''),
            ]).lower()

            if any(kw in clues for kw in ['card number', 'cardnumber', 'cc-number', 'رقم البطاقة', 'رقم الكرت', 'pan', 'card_number']):
                inp.click()
                time.sleep(0.3)
                for ch in card_num:
                    inp.type(ch, delay=random.randint(50, 120))
                filled += 1
                log_fn(f"  💳 Card number: {card_num[:4]}****{card_num[-4:]}")
            elif any(kw in clues for kw in ['expir', 'exp', 'mm/yy', 'mm/yyyy', 'انتهاء', 'صلاحية', 'cc-exp', 'valid']):
                inp.click()
                time.sleep(0.3)
                inp.fill(expiry)
                filled += 1
                log_fn(f"  💳 Expiry: {expiry}")
            elif any(kw in clues for kw in ['cvv', 'cvc', 'security', 'رمز الأمان', 'رمز التحقق', 'cc-csc', 'csv']):
                inp.click()
                time.sleep(0.3)
                for ch in cvv:
                    inp.type(ch, delay=random.randint(50, 120))
                filled += 1
                log_fn(f"  💳 CVV: ***")
            elif any(kw in clues for kw in ['cardholder', 'card holder', 'name on card', 'holder', 'حامل البطاقة', 'cc-name']):
                inp.click()
                time.sleep(0.3)
                inp.fill(holder)
                filled += 1
                log_fn(f"  💳 Holder: {holder}")
        except:
            continue

    # Check select dropdowns for month/year
    selects = page.locator('select:visible').all()
    for sel in selects:
        try:
            sel_name = ' '.join([
                (sel.get_attribute('name') or ''),
                (sel.get_attribute('id') or ''),
                (sel.get_attribute('aria-label') or ''),
            ]).lower()

            if any(kw in sel_name for kw in ['month', 'mm', 'شهر']):
                options = sel.locator('option').all()
                if len(options) > 1:
                    idx = random.randint(1, min(12, len(options)-1))
                    sel.select_option(index=idx)
                    filled += 1
                    log_fn(f"  💳 Expiry month selected")
            elif any(kw in sel_name for kw in ['year', 'yy', 'سنة']):
                options = sel.locator('option').all()
                if len(options) > 1:
                    idx = random.randint(1, min(len(options)-1, 5))
                    sel.select_option(index=idx)
                    filled += 1
                    log_fn(f"  💳 Expiry year selected")
        except:
            continue

    if filled > 0:
        log_fn(f"💳 Filled {filled} card fields")
    return filled > 0


def fill_card_fields_in_frame(frame, log_fn=print):
    """Fill credit card fields inside an iframe"""
    card_num = gen_card_number()
    expiry = gen_card_expiry()
    cvv = gen_cvv()
    holder = gen_cardholder_name()
    filled = 0

    inputs = frame.locator('input:visible').all()
    for inp in inputs:
        try:
            input_type = (inp.get_attribute('type') or 'text').lower()
            if input_type in ['hidden', 'submit', 'button', 'checkbox', 'radio']:
                continue

            clues = ' '.join([
                (inp.get_attribute('placeholder') or ''),
                (inp.get_attribute('name') or ''),
                (inp.get_attribute('id') or ''),
                (inp.get_attribute('aria-label') or ''),
                (inp.get_attribute('autocomplete') or ''),
            ]).lower()

            if any(kw in clues for kw in ['card number', 'cardnumber', 'cc-number', 'pan', 'card_number', 'رقم البطاقة']):
                inp.click()
                time.sleep(0.3)
                for ch in card_num:
                    inp.type(ch, delay=random.randint(50, 120))
                filled += 1
                log_fn(f"  💳 [iframe] Card: {card_num[:4]}****{card_num[-4:]}")
            elif any(kw in clues for kw in ['expir', 'exp', 'mm/yy', 'انتهاء', 'cc-exp', 'valid']):
                inp.click()
                time.sleep(0.3)
                inp.fill(expiry)
                filled += 1
                log_fn(f"  💳 [iframe] Expiry: {expiry}")
            elif any(kw in clues for kw in ['cvv', 'cvc', 'security', 'cc-csc', 'csv', 'رمز']):
                inp.click()
                time.sleep(0.3)
                for ch in cvv:
                    inp.type(ch, delay=random.randint(50, 120))
                filled += 1
                log_fn(f"  💳 [iframe] CVV: ***")
            elif any(kw in clues for kw in ['cardholder', 'holder', 'name on card', 'cc-name', 'حامل']):
                inp.click()
                time.sleep(0.3)
                inp.fill(holder)
                filled += 1
                log_fn(f"  💳 [iframe] Holder: {holder}")
        except:
            continue

    if filled > 0:
        log_fn(f"💳 [iframe] Filled {filled} card fields")
    return filled > 0


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

    print(f"🚀 Smart Bot v22 starting - URL: {target_url} | Duration: {duration_min}min | Instances: {num_instances}")
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

                    try:
                        # STEP 1: Open the target URL
                        print(f"🌐 Opening {target_url}...")
                        page.goto(target_url, wait_until='networkidle', timeout=60000)
                        time.sleep(random.uniform(2, 4))

                        # Simulate human behavior
                        page.mouse.move(random.randint(100, 500), random.randint(100, 300))
                        time.sleep(random.uniform(0.5, 1))

                        # STEP 2: Analyze the page
                        page_type, page_info = analyze_page_content(page, log_fn=print)
                        
                        if page_type == 'error':
                            print("🚫 Page blocked or error - skipping")
                            total_errors += 1
                            continue

                        # STEP 3: Handle up to 5 pages (form → summary → payment → confirmation)
                        max_pages = 5
                        for page_num in range(1, max_pages + 1):
                            if time.time() >= end_time:
                                break

                            if page_num > 1:
                                # Re-analyze page after navigation
                                time.sleep(random.uniform(2, 4))
                                page_type, page_info = analyze_page_content(page, log_fn=print)
                                print(f"\n📄 Page {page_num}: {page.url} (type: {page_type})")

                            if page_type == 'form':
                                # Fill the form
                                filled_data, total_filled = fill_form_on_page(page, log_fn=print)
                                
                                if total_filled > 0:
                                    # Click submit/next
                                    submitted = click_submit_button(page, log_fn=print)
                                    
                                    if submitted:
                                        time.sleep(random.uniform(3, 5))
                                        try:
                                            page.wait_for_load_state('networkidle', timeout=15000)
                                        except:
                                            pass
                                        
                                        # Check for validation errors
                                        try:
                                            error_selectors = ['.error', '.error-message', '.alert-danger', '.invalid-feedback',
                                                             '.field-error', '.form-error', '[class*="error"]', '[class*="invalid"]',
                                                             '.text-danger', '.text-red', '.validation-error']
                                            errors_found = []
                                            for selector in error_selectors:
                                                try:
                                                    error_els = page.locator(selector + ':visible').all()
                                                    for el in error_els:
                                                        try:
                                                            err_text = el.inner_text().strip()
                                                            if err_text and len(err_text) > 2:
                                                                errors_found.append(err_text[:100])
                                                        except:
                                                            pass
                                                except:
                                                    pass
                                            if errors_found:
                                                print(f"⚠️ Validation errors: {'; '.join(errors_found[:3])}")
                                        except:
                                            pass
                                        
                                        if page_num == 1:
                                            total_submissions += 1
                                            entry = {
                                                'id': total_submissions,
                                                'time': datetime.now().strftime('%H:%M:%S'),
                                                'name': filled_data.get('name', '-'),
                                                'national_id': filled_data.get('national_id', '-'),
                                                'phone': filled_data.get('phone', '-'),
                                                'email': filled_data.get('email', '-'),
                                                'status': 'page1_done'
                                            }
                                            update_status(entry=entry)
                                            print(f"✅ Page 1 filled! (Submission #{total_submissions})")
                                        else:
                                            print(f"✅ Page {page_num} filled!")
                                        
                                        # Continue to next page
                                        continue
                                    else:
                                        print(f"⚠️ Could not submit page {page_num}")
                                        break
                                else:
                                    print(f"⚠️ No fields filled on page {page_num}")
                                    break

                            elif page_type == 'payment':
                                payment_success = handle_payment_page(page, log_fn=print)
                                if payment_success:
                                    print("✅ Payment completed!")
                                    # Update the last entry status
                                    if recent_entries:
                                        recent_entries[0]['status'] = 'payment_done'
                                        update_status()
                                else:
                                    print("⚠️ Payment attempted but no card fields found")
                                break  # Payment is usually the last step

                            elif page_type == 'summary':
                                print("📄 Summary page - clicking action button...")
                                clicked = click_action_button(page, log_fn=print)
                                if clicked:
                                    time.sleep(random.uniform(3, 5))
                                    try:
                                        page.wait_for_load_state('networkidle', timeout=15000)
                                    except:
                                        pass
                                    print(f"✅ Summary page handled, moving to next...")
                                    # Update status
                                    if recent_entries:
                                        recent_entries[0]['status'] = 'summary_done'
                                        update_status()
                                    continue
                                else:
                                    break

                            elif page_type == 'success':
                                print("🎉 Booking confirmed!")
                                if recent_entries:
                                    recent_entries[0]['status'] = 'confirmed'
                                    update_status()
                                break

                            else:
                                # Unknown page - try to find any action button
                                print(f"❓ Unknown page type - trying to find action button...")
                                clicked = click_action_button(page, log_fn=print)
                                if clicked:
                                    time.sleep(random.uniform(3, 5))
                                    try:
                                        page.wait_for_load_state('networkidle', timeout=15000)
                                    except:
                                        pass
                                    continue
                                else:
                                    print("⚠️ No action possible on this page")
                                    break

                    except Exception as e:
                        total_errors += 1
                        print(f"❌ Instance error: {str(e)[:100]}")

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
                print(f"❌ Browser error: {str(e)[:100]}")
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
