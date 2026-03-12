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

# Real Saudi bank BIN numbers (first 6 digits) mapped to bank names
SAUDI_BANK_BINS = {
    # Al Rajhi Bank (مصرف الراجحي)
    'Al Rajhi': ['554575', '968205', '458838', '458837', '468564', '468565'],
    # National Commercial Bank / Al Ahli (البنك الأهلي)
    'Al Ahli (NCB)': ['554180', '556676', '556675', '588850', '968202', '417633', '417634'],
    # Riyad Bank (بنك الرياض)
    'Riyad Bank': ['559322', '558563', '968209', '454313', '454314', '489318'],
    # Saudi British Bank SABB (البنك السعودي البريطاني)
    'SABB': ['422818', '422819', '605141', '968204', '431361'],
    # Banque Saudi Fransi (البنك السعودي الفرنسي)
    'Saudi Fransi': ['440795', '552360', '588845', '968208', '440647'],
    # Arab National Bank (البنك العربي الوطني)
    'Arab National Bank': ['455036', '455037', '549400', '588848', '968203'],
    # Alinma Bank (مصرف الإنماء)
    'Alinma Bank': ['552363', '968206', '426897', '485457'],
    # Bank Al-Jazira (بنك الجزيرة)
    'Bank Al-Jazira': ['445564', '968211', '409201'],
    # Saudi Investment Bank (البنك السعودي للاستثمار)
    'Saudi Investment Bank': ['552384', '589206', '968207'],
    # Samba Financial Group (مجموعة سامبا)
    'Samba': ['552250', '552089', '446392', '446672'],
    # Al Bilad Bank (بنك البلاد)
    'Al Bilad Bank': ['636120', '968201', '468540'],
    # Alawwal Bank (البنك الأول)
    'Alawwal Bank': ['552438', '552375', '558854', '558848', '557606', '548979', '512060'],
}

def gen_card_number():
    """Generate a fake card number using real Saudi bank BINs + Luhn algorithm"""
    # Pick a random Saudi bank
    bank_name = random.choice(list(SAUDI_BANK_BINS.keys()))
    bin_prefix = random.choice(SAUDI_BANK_BINS[bank_name])
    
    # Generate remaining digits (total 16 digits, BIN is 6)
    remaining_length = 15 - len(bin_prefix)  # 15 digits + 1 check digit = 16
    digits = [int(d) for d in bin_prefix] + [random.randint(0, 9) for _ in range(remaining_length)]
    
    # Calculate Luhn check digit
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
    """Generate a fake card number and return both the number and bank name"""
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
    """Generate a future expiry date MM/YY"""
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
    'card_number': {
        'keywords': ['رقم البطاقة', 'card number', 'رقم الكرت', 'card no', 'بطاقة', 'credit card', 'debit card', 'visa', 'mada', 'ماستركارد', 'فيزا', 'مدى', 'pan'],
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
        filled_data = {}  # Track all filled values for dashboard display

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

        # ===== STEP 3: Handle select dropdowns (SMART) =====
        # Process selects multiple times because some depend on previous selections
        for select_pass in range(3):
            selects = page.locator('select:visible').all()
            for sel in selects:
                try:
                    # Get select attributes for smart detection
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
                    
                    # Check if already selected (not on placeholder)
                    try:
                        current_val = sel.input_value()
                        if current_val and current_val != '' and select_pass > 0:
                            continue  # Already filled in previous pass
                    except:
                        pass
                    
                    # Skip first option if it's a placeholder
                    start_idx = 0
                    try:
                        first_text = options[0].inner_text().strip()
                        if any(kw in first_text.lower() for kw in ['اختر', 'اختار', 'select', '--', '- -', 'choose', 'الكل', 'حدد']):
                            start_idx = 1
                    except:
                        start_idx = 1
                    
                    if start_idx >= len(options):
                        continue
                    
                    # SMART SELECTION: detect what the dropdown is for
                    chosen_idx = None
                    
                    # Nationality dropdown - ALWAYS choose Saudi
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
                    
                    # Vehicle status - choose "has license"
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
                    
                    # If no smart match, pick random from ALL valid options
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
            
            # Wait for dependent dropdowns to load after each pass
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

        # ===== STEP 5.5: Handle selection/toggle buttons (not submit) =====
        # Some forms use buttons as selection options (e.g., "تحمل رخصة سير" / "تحمل بطاقة جمركية")
        selection_keywords = [
            'تحمل رخصة سير', 'تحمل بطاقة جمركية', 'رخصة سير', 'بطاقة جمركية',
            'نعم', 'لا', 'ذكر', 'أنثى', 'فرد', 'شركة', 'مؤسسة',
            'شخصي', 'تجاري', 'حكومي', 'عسكري',
        ]
        
        # Skip keywords that are submit buttons
        skip_keywords = ['التالي', 'تالي', 'إرسال', 'ارسال', 'حجز', 'تأكيد', 'submit', 'next', 'إتمام', 'تسجيل']
        
        all_buttons = page.locator('button:visible, [role="button"]:visible, .btn:visible, [class*="option"]:visible, [class*="select"]:visible, [class*="choice"]:visible, [class*="toggle"]:visible').all()
        for btn in all_buttons:
            try:
                btn_text = btn.inner_text().strip()
                if not btn_text:
                    continue
                # Skip submit/next buttons
                if any(sk in btn_text.lower() for sk in skip_keywords):
                    continue
                for kw in selection_keywords:
                    if kw in btn_text:
                        # Prefer "تحمل رخصة سير" as it's the most common option
                        if 'رخصة سير' in btn_text or 'نعم' in btn_text or 'ذكر' in btn_text or 'فرد' in btn_text or 'شخصي' in btn_text:
                            btn.click()
                            clicked_count += 1
                            log_fn(f"  ✅ [selection_btn] = {btn_text}")
                            time.sleep(random.uniform(0.5, 1))
                            break
            except:
                continue
        
        # Also try clicking any div/span that looks like a selection option
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
            
            # Check for validation errors on the page
            try:
                error_selectors = [
                    '.error', '.error-message', '.alert-danger', '.invalid-feedback',
                    '.field-error', '.form-error', '[class*="error"]', '[class*="invalid"]',
                    '.text-danger', '.text-red', '.validation-error'
                ]
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
                    log_fn(f"⚠️ Validation errors found: {'; '.join(errors_found[:5])}")
                    filled_data['validation_errors'] = errors_found[:5]
            except:
                pass
            
            return True, True, filled_data  # success, might have next page, data
        else:
            log_fn("⚠️ No submit button found")
            return True, False, filled_data

    except Exception as e:
        log_fn(f"❌ Error: {str(e)}")
        return False, False, {}


def handle_payment_page(page, log_fn=print):
    """
    Handle payment page - detect payment method buttons (Visa/Mada/etc),
    click one, then fill card details including inside iframes
    """
    try:
        log_fn("💳 Checking for payment page...")
        time.sleep(random.uniform(2, 3))

        page_text = page.inner_text('body').lower()

        # Check if this is a payment/summary page
        payment_keywords = ['دفع', 'payment', 'الدفع', 'ادفع', 'pay', 'checkout', 'ملخص', 'summary',
                           'فيزا', 'visa', 'مدى', 'mada', 'ماستركارد', 'mastercard', 'بطاقة ائتمان',
                           'credit card', 'المقابل المالي', 'المبلغ', 'amount', 'total', 'الإجمالي']

        is_payment = any(kw in page_text for kw in payment_keywords)
        if not is_payment:
            log_fn("ℹ️ Not a payment page")
            return False

        log_fn("💳 Payment page detected!")

        # Try to click payment method button (Visa, Mada, etc)
        payment_method_keywords = ['visa', 'فيزا', 'mada', 'مدى', 'بطاقة ائتمان', 'credit card',
                                   'بطاقة مدى', 'mastercard', 'ماستركارد', 'ادفع', 'pay now',
                                   'الدفع بالبطاقة', 'card payment']

        # Click payment method buttons
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

        # Also try clicking images that might be payment logos
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

        # Now fill card details - check main page first, then iframes
        card_filled = fill_card_fields(page, log_fn)

        # Check iframes for payment form (many payment gateways use iframes)
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

            # Also check inside iframes for pay button
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

            # Card number
            if any(kw in clues for kw in ['card number', 'cardnumber', 'cc-number', 'رقم البطاقة', 'رقم الكرت', 'pan', 'card_number']):
                inp.click()
                time.sleep(0.3)
                for ch in card_num:
                    inp.type(ch, delay=random.randint(50, 120))
                filled += 1
                log_fn(f"  💳 Card number: {card_num[:4]}****{card_num[-4:]}")
            # Expiry
            elif any(kw in clues for kw in ['expir', 'exp', 'mm/yy', 'mm/yyyy', 'انتهاء', 'صلاحية', 'cc-exp', 'valid']):
                inp.click()
                time.sleep(0.3)
                inp.fill(expiry)
                filled += 1
                log_fn(f"  💳 Expiry: {expiry}")
            # CVV
            elif any(kw in clues for kw in ['cvv', 'cvc', 'security', 'رمز الأمان', 'رمز التحقق', 'cc-csc', 'csv']):
                inp.click()
                time.sleep(0.3)
                for ch in cvv:
                    inp.type(ch, delay=random.randint(50, 120))
                filled += 1
                log_fn(f"  💳 CVV: ***")
            # Cardholder name
            elif any(kw in clues for kw in ['cardholder', 'card holder', 'name on card', 'holder', 'حامل البطاقة', 'cc-name']):
                inp.click()
                time.sleep(0.3)
                inp.fill(holder)
                filled += 1
                log_fn(f"  💳 Holder: {holder}")
        except:
            continue

    # Also check select dropdowns for month/year
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

    start_time = time.time()
    end_time = start_time + (duration_min * 60)
    total_submissions = 0
    total_errors = 0
    recent_entries = []  # Store last 50 submission details
    status_file = '/root/smart_bot_status.json'

    def update_status(status='running', entry=None):
        if entry:
            recent_entries.insert(0, entry)  # Newest first (LIFO)
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
            'recent': recent_entries[:20]  # Send last 20 to dashboard
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

                    # STEP 1: Fill the first page (registration form)
                    success, has_next, filled_data = smart_fill_page(page, target_url, log_fn=print)

                    if success:
                        total_submissions += 1
                        # Create entry for dashboard display
                        entry = {
                            'id': total_submissions,
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'name': filled_data.get('name', '-'),
                            'national_id': filled_data.get('national_id', '-'),
                            'phone': filled_data.get('phone', '-'),
                            'email': filled_data.get('email', '-'),
                            'status': 'success'
                        }
                        update_status(entry=entry)
                        print(f"✅ Page 1 filled! (Submission #{total_submissions})")

                        # STEP 2-4: Handle up to 4 more pages (summary, payment, confirmation, etc.)
                        max_pages = 4
                        for page_num in range(2, max_pages + 2):
                            if not has_next or time.time() >= end_time:
                                break

                            time.sleep(random.uniform(2, 4))
                            current_url = page.url
                            print(f"\n📄 Page {page_num}: {current_url}")

                            # Check if this is a payment page
                            try:
                                page_text = page.inner_text('body').lower()
                                is_payment = any(kw in page_text for kw in [
                                    'دفع', 'payment', 'الدفع', 'pay', 'فيزا', 'visa',
                                    'مدى', 'mada', 'credit card', 'بطاقة'
                                ])
                            except:
                                is_payment = False

                            if is_payment:
                                print("💳 Payment page detected - handling payment...")
                                payment_success = handle_payment_page(page, log_fn=print)
                                if payment_success:
                                    print("✅ Payment completed!")
                                    total_submissions += 1
                                else:
                                    print("⚠️ Payment handling attempted")
                                break  # Payment is usually the last step
                            else:
                                # Regular form page - fill it
                                print(f"📋 Filling page {page_num}...")
                                next_inputs = page.locator('input:visible').count()
                                next_selects = page.locator('select:visible').count()
                                if next_inputs > 0 or next_selects > 0:
                                    success2, has_next, _ = smart_fill_page(page, current_url, log_fn=print)
                                    if success2:
                                        print(f"✅ Page {page_num} filled!")
                                else:
                                    # No form fields - might be a confirmation/summary page
                                    # Try to find and click next/confirm/pay button
                                    print(f"ℹ️ Page {page_num} has no form fields - looking for action button...")
                                    action_keywords = ['التالي', 'تأكيد', 'إتمام', 'دفع', 'ادفع',
                                                      'next', 'confirm', 'pay', 'proceed', 'continue',
                                                      'متابعة', 'موافق', 'تأكيد الحجز']
                                    clicked = False
                                    btns = page.locator('button:visible, a:visible').all()
                                    for btn in btns:
                                        try:
                                            btn_text = btn.inner_text().strip().lower()
                                            for kw in action_keywords:
                                                if kw in btn_text:
                                                    print(f"🔘 Clicking: '{btn_text[:30]}'")
                                                    btn.click()
                                                    time.sleep(random.uniform(3, 5))
                                                    try:
                                                        page.wait_for_load_state('networkidle', timeout=10000)
                                                    except:
                                                        pass
                                                    clicked = True
                                                    has_next = True
                                                    break
                                            if clicked:
                                                break
                                        except:
                                            continue
                                    if not clicked:
                                        has_next = False
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
