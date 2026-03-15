"""
Smart Universal Form Bot v39 - React State Sync + Fixed Classification
Uses Patchright (undetected Chrome) + dynamic form field detection
Works on ANY booking/registration site - no hardcoded placeholders or domains
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
import mimetypes
from datetime import datetime, timedelta
from urllib.parse import urlparse

os.environ.setdefault('DISPLAY', ':99')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# Fix stdout/stderr encoding for Arabic text
import io
import sys as _sys
if hasattr(_sys.stdout, 'buffer'):
    _sys.stdout = io.TextIOWrapper(_sys.stdout.buffer, encoding='utf-8', errors='replace')
    _sys.stderr = io.TextIOWrapper(_sys.stderr.buffer, encoding='utf-8', errors='replace')

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


# ============ FIELD CLASSIFICATION KEYWORDS ============
# Each category has Arabic + English keywords to match against placeholder, label, name, id, aria-label

FIELD_KEYWORDS = {
    'name': {
        'ar': ['الاسم', 'الإسم', 'اسم', 'إسم', 'ادخل الاسم', 'إدخل الإسم', 'الاسم الكامل', 'اسم المالك', 'اسم صاحب'],
        'en': ['name', 'full_name', 'fullname', 'owner_name', 'applicant'],
        'exclude': ['مستخدم', 'user', 'حامل', 'holder', 'cardholder', 'card', 'بطاقة'],
    },
    'national_id': {
        'ar': ['الهوية', 'هوية', 'رقم الهوية', 'هوية وطنية', 'الهوية الوطنية', 'رقم الإقامة', 'هوية/إقامة', 'السجل المدني'],
        'en': ['national_id', 'identity', 'id_number', 'iqama', 'civil_id', 'national'],
        'exclude': [],
    },
    'phone': {
        'ar': ['الجوال', 'جوال', 'رقم الجوال', 'الهاتف', 'هاتف', 'رقم الهاتف', 'موبايل', 'أكتب رقم الجوال', 'رقم التواصل'],
        'en': ['phone', 'mobile', 'tel', 'telephone', 'cell', 'contact_number'],
        'exclude': [],
    },
    'email': {
        'ar': ['البريد', 'بريد', 'الإيميل', 'إيميل', 'البريد الإلكتروني', 'بريد إلكتروني'],
        'en': ['email', 'e-mail', 'mail'],
        'exclude': [],
    },
    'plate_number': {
        'ar': ['أرقام اللوحة', 'رقم اللوحة', 'الأرقام', 'أدخل الأرقام', 'أرقام'],
        'en': ['plate_number', 'plate_digits', 'plate_num', 'plate'],
        'exclude': ['حروف', 'letter'],
    },
    'city': {
        'ar': ['المدينة', 'مدينة'],
        'en': ['city'],
        'exclude': [],
    },
    'address': {
        'ar': ['العنوان', 'عنوان'],
        'en': ['address', 'street'],
        'exclude': ['بريد', 'email', 'url', 'رابط'],
    },
    'date_of_birth': {
        'ar': ['تاريخ الميلاد', 'تاريخ ميلاد', 'الميلاد', 'ميلاد'],
        'en': ['birth', 'dob', 'date_of_birth'],
        'exclude': [],
    },
    'inspection_date': {
        'ar': ['تاريخ الفحص', 'تاريخ', 'التاريخ', 'موعد الفحص'],
        'en': ['date', 'inspection_date', 'appointment_date', 'schedule'],
        'exclude': ['ميلاد', 'birth', 'انتهاء', 'expir', 'commissioner', 'مفوض'],
    },
    'delegate_name': {
        'ar': ['المفوض', 'مفوض', 'أسم المفوض', 'اسم المفوض', 'الوكيل', 'وكيل', 'المندوب', 'مندوب'],
        'en': ['delegate', 'representative', 'agent_name', 'authorized'],
        'exclude': ['date', 'تاريخ', 'phone', 'جوال', 'هوية', 'id'],
    },
}

# Keywords for SELECT dropdowns
SELECT_KEYWORDS = {
    'nationality': {
        'ar': ['الجنسية', 'جنسية'],
        'en': ['nationality', 'nation'],
        'preferred': 'السعودية',
    },
    'country': {
        'ar': ['بلد التسجيل', 'البلد', 'بلد', 'الدولة'],
        'en': ['country', 'registration_country'],
        'preferred': 'السعودية',
    },
    'region': {
        'ar': ['المنطقة', 'منطقة'],
        'en': ['region', 'area'],
        'preferred': None,
    },
    'center': {
        'ar': ['مركز الفحص', 'المركز', 'مركز', 'الفرع', 'فرع'],
        'en': ['center', 'branch', 'station', 'inspection_center'],
        'preferred': None,
    },
    'vehicle_type': {
        'ar': ['نوع المركبة', 'المركبة', 'نوع السيارة'],
        'en': ['vehicle_type', 'car_type'],
        'preferred': None,
    },
    'registration_type': {
        'ar': ['نوع التسجيل', 'التسجيل'],
        'en': ['registration_type', 'reg_type'],
        'preferred': None,
    },
    'time_slot': {
        'ar': ['وقت الفحص', 'الوقت', 'وقت', 'الموعد'],
        'en': ['time', 'slot', 'appointment_time', 'time_slot'],
        'preferred': None,
    },
    'service': {
        'ar': ['خدمة الفحص', 'الخدمة', 'خدمة', 'نوع الخدمة'],
        'en': ['service', 'service_type', 'inspection_type'],
        'preferred': None,
    },
    'vehicle_condition': {
        'ar': ['حالة المركبة', 'حالة السيارة', 'الحالة'],
        'en': ['vehicle_condition', 'car_condition', 'condition'],
        'preferred': None,
    },
    'plate_letter': {
        'ar': ['حرف لوحة', 'حرف اللوحة', 'الحرف'],
        'en': ['plate_letter', 'letter'],
        'preferred': None,
    },
}


# ============ DYNAMIC FIELD DETECTION ============

def classify_input_field(clues):
    """Classify an input field based on all available clues (placeholder, label, name, id, aria-label)"""
    clues_lower = clues.lower()
    
    for field_type, keywords in FIELD_KEYWORDS.items():
        # Check exclusions first - if any exclusion matches, skip this field_type entirely
        excluded = False
        for exc in keywords.get('exclude', []):
            if exc in clues_lower:
                excluded = True
                break
        if excluded:
            continue
        
        # Check Arabic keywords
        for kw in keywords['ar']:
            if kw in clues:
                return field_type
        
        # Check English keywords
        for kw in keywords['en']:
            if kw in clues_lower:
                return field_type
    
    # Fallback: check for commissioner-date specifically
    if 'commissioner-date' in clues_lower or 'commissioner_date' in clues_lower:
        return 'date_of_birth'
    
    # Fallback: check input type
    if 'type="email"' in clues_lower or 'type:email' in clues_lower:
        return 'email'
    if 'type="tel"' in clues_lower or 'type:tel' in clues_lower:
        return 'phone'
    
    return 'unknown'


def classify_select_field(clues):
    """Classify a SELECT dropdown based on its label/name/id"""
    clues_lower = clues.lower()
    
    for field_type, keywords in SELECT_KEYWORDS.items():
        for kw in keywords['ar']:
            if kw in clues:
                return field_type, keywords.get('preferred')
        for kw in keywords['en']:
            if kw in clues_lower:
                return field_type, keywords.get('preferred')
    
    return 'unknown', None


def get_field_value(field_type, data):
    """Get the appropriate value for a classified field type"""
    if field_type == 'name':
        return data['name']
    elif field_type == 'national_id':
        return data['national_id']
    elif field_type == 'phone':
        return data['phone']
    elif field_type == 'email':
        return data['email']
    elif field_type == 'plate_number':
        return data['plate_num']
    elif field_type == 'city':
        return random.choice(SAUDI_CITIES)
    elif field_type == 'address':
        return f"شارع {random.randint(1, 50)}، حي {random.choice(['النزهة', 'الروضة', 'العليا', 'السلامة', 'الحمراء', 'المروج'])}"
    elif field_type == 'date_of_birth':
        year = random.randint(1970, 2000)
        month = f"{random.randint(1, 12):02d}"
        day = f"{random.randint(1, 28):02d}"
        return f"{year}-{month}-{day}"
    elif field_type == 'inspection_date':
        # Generate a date in the near future (next 1-14 days)
        future = datetime.now() + timedelta(days=random.randint(1, 14))
        return future.strftime('%Y-%m-%d')
    elif field_type == 'delegate_name':
        # Use the same person's name as delegate
        return data.get('name', gen_name())
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
                page.mouse.move(random.randint(400, 600), random.randint(300, 500))
                time.sleep(random.uniform(0.3, 0.8))
                page.mouse.move(170, 275)
                time.sleep(random.uniform(0.3, 0.6))
                page.mouse.click(170, 275)
                print(f"  🖱️ Clicked Turnstile ({elapsed}s)", flush=True)
            except:
                pass
            
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


# ============ DYNAMIC FORM FILLING ============

def fill_all_empty_fields(page, data=None):
    """Fill ALL empty visible inputs and selects using smart classification + Playwright fill()"""
    if data is None:
        data = {
            'name': gen_name(),
            'national_id': gen_saudi_id(),
            'phone': gen_saudi_phone(),
            'email': gen_email(),
            'plate_num': gen_plate_number(),
        }
    
    filled = 0
    
    # STEP A: Get all empty input fields info via JS
    try:
        empty_inputs = page.evaluate("""() => {
            const fields = [];
            const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"])');
            let visIdx = 0;
            for (const inp of inputs) {
                if (inp.offsetParent === null) continue;
                if (inp.value && inp.value.trim() !== '') { visIdx++; continue; }
                
                const ph = inp.getAttribute('placeholder') || '';
                const name = inp.getAttribute('name') || '';
                const id = inp.getAttribute('id') || '';
                const type = inp.getAttribute('type') || 'text';
                const ac = inp.getAttribute('autocomplete') || '';
                const aria = inp.getAttribute('aria-label') || '';
                const maxlen = inp.getAttribute('maxlength') || '';
                
                let labelText = '';
                if (id) {
                    const lbl = document.querySelector('label[for="' + id + '"]');
                    if (lbl) labelText = lbl.innerText.trim();
                }
                if (!labelText) {
                    const parent = inp.closest('.mb-4, .mb-3, .mb-2, .form-group, [class*="form"], [class*="field"]');
                    if (parent) {
                        const lbl = parent.querySelector('label, .label, h6, h5');
                        if (lbl) labelText = lbl.innerText.trim();
                    }
                }
                
                fields.push({
                    visibleIndex: visIdx,
                    placeholder: ph,
                    name: name,
                    id: id,
                    type: type,
                    autocomplete: ac,
                    ariaLabel: aria,
                    label: labelText,
                    maxlength: maxlen,
                    selector: id ? '#' + CSS.escape(id) : (name ? 'input[name="' + name + '"]' : null)
                });
                visIdx++;
            }
            return fields;
        }""")
        
        if empty_inputs:
            for field in empty_inputs:
                clues = f"{field['placeholder']} {field['label']} {field['name']} {field['id']} {field['autocomplete']} {field['ariaLabel']} type:{field['type']}"
                field_type = classify_input_field(clues)
                
                if field_type == 'unknown':
                    maxlen = field.get('maxlength', '')
                    if maxlen == '10':
                        field_type = 'national_id'
                    elif maxlen == '4':
                        field_type = 'plate_number'
                    elif field.get('type') == 'date':
                        field_type = 'inspection_date'
                    elif field.get('type') == 'email':
                        field_type = 'email'
                    elif field.get('type') == 'tel':
                        field_type = 'phone'
                    else:
                        all_clues = f"{field['placeholder']} {field['label']} {field['name']} {field['id']}"
                        if any(w in all_clues for w in ['commissioner', 'مفوض']):
                            field_type = 'date_of_birth'
                        elif any(w in all_clues for w in ['\u062a\u0627\u0631\u064a\u062e', 'date', '\u0645\u0648\u0639\u062f']):
                            field_type = 'inspection_date'
                        else:
                            print(f"    [refill] Unknown input: ph='{field['placeholder'][:20]}' label='{field['label'][:20]}'", flush=True)
                            continue
                
                value = get_field_value(field_type, data)
                if not value:
                    continue
                
                try:
                    selector = field.get('selector')
                    if selector:
                        el = page.locator(selector).first
                    else:
                        el = page.locator('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"]):visible').nth(field['visibleIndex'])
                    
                    if el.is_visible():
                        if field.get('type') == 'date':
                            el.focus()
                            el.fill(value)
                            el.evaluate("""(el) => {
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""")
                        else:
                            el.click()
                            time.sleep(random.uniform(0.1, 0.3))
                            el.press('Control+a')
                            time.sleep(0.1)
                            el.type(value, delay=random.randint(20, 50))
                        el.press('Tab')
                        time.sleep(random.uniform(0.2, 0.5))
                        filled += 1
                        print(f"    [refill] {field_type}: {value[:25]}", flush=True)
                except Exception as e:
                    print(f"    [refill] Error {field_type}: {str(e)[:50]}", flush=True)
    except Exception as e:
        print(f"    [refill] Input scan error: {str(e)[:80]}", flush=True)
    
    # STEP B: Fill empty selects using smart classification + Playwright select_option
    try:
        empty_sels = page.evaluate("""() => {
            const result = [];
            const selects = document.querySelectorAll('select');
            let visIdx = 0;
            for (const sel of selects) {
                if (sel.offsetParent === null) continue;
                const currentOpt = sel.options[sel.selectedIndex];
                const optText = currentOpt ? currentOpt.text.trim() : '';
                const optVal = sel.value || '';
                
                const placeholderWords = ['\u0627\u062e\u062a\u0631', '\u0627\u062e\u062a\u064a\u0627\u0631', 'Select', 'Choose', '--', '---'];
                const isPlaceholder = !optVal || optVal === '' || optVal === '-' || optVal === '0' ||
                    placeholderWords.some(pw => optText.includes(pw)) || optText === '';
                
                if (isPlaceholder) {
                    // Get label for classification
                    const name = sel.getAttribute('name') || '';
                    const id = sel.getAttribute('id') || '';
                    const aria = sel.getAttribute('aria-label') || '';
                    let labelText = '';
                    if (id) {
                        const lbl = document.querySelector('label[for="' + id + '"');
                        if (lbl) labelText = lbl.innerText.trim();
                    }
                    if (!labelText) {
                        const parent = sel.closest('.mb-4, .mb-3, .mb-2, .form-group, [class*="form"], [class*="field"]');
                        if (parent) {
                            const lbl = parent.querySelector('label, .label, h6, h5');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                    }
                    if (!labelText) {
                        const parent = sel.parentElement;
                        if (parent) {
                            const lbl = parent.querySelector('label');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                    }
                    
                    const opts = Array.from(sel.options).filter(o => 
                        o.value && o.value !== '' && o.value !== '-' && o.value !== '0' &&
                        !placeholderWords.some(pw => o.text.includes(pw))).map(o => ({value: o.value, text: o.text.trim()}));
                    
                    if (opts.length > 0) {
                        result.push({ visIdx: visIdx, label: labelText, name: name, id: id, ariaLabel: aria, options: opts });
                    }
                }
                visIdx++;
            }
            return result;
        }""")
        if empty_sels:
            for es in empty_sels:
                try:
                    # Classify the select to pick the right value
                    clues = f"{es.get('label','')} {es.get('name','')} {es.get('id','')} {es.get('ariaLabel','')}"
                    field_type, preferred = classify_select_field(clues)
                    
                    # Choose option: prefer the preferred value, else random
                    chosen = None
                    if preferred:
                        for opt in es['options']:
                            if preferred in opt.get('text', '') or preferred in opt.get('value', ''):
                                chosen = opt
                                break
                    if not chosen:
                        chosen = random.choice(es['options'])
                    
                    sel_el = page.locator('select:visible').nth(es['visIdx'])
                    sel_el.select_option(value=chosen['value'])
                    # Trigger React onChange event
                    sel_el.evaluate("""(el) => {
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                        nativeSetter.call(el, el.value);
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                    }""")
                    filled += 1
                    print(f"    [refill] {field_type}: {chosen['text'][:30]}", flush=True)
                    time.sleep(random.uniform(0.3, 0.6))
                    
                    # Wait for dependent dropdowns if region/country changed
                    if field_type in ('region', 'country', 'nationality'):
                        time.sleep(random.uniform(1.5, 2.5))
                except:
                    pass
    except:
        pass
    
    # Also handle React custom dropdown buttons with placeholder text
    try:
        placeholder_btns = page.evaluate("""() => {
            const results = [];
            const buttons = document.querySelectorAll('button[role="combobox"], button[data-state], button[aria-expanded]');
            for (const btn of buttons) {
                if (btn.offsetParent === null) continue;
                const text = btn.innerText.trim();
                if (text.includes('\u0623\u062e\u062a\u0631') || text.includes('\u0627\u062e\u062a\u0631') || text.includes('\u0627\u062e\u062a\u064a\u0627\u0631')) {
                    results.push({ text: text, rect: btn.getBoundingClientRect() });
                }
            }
            if (results.length === 0) {
                const allBtns = document.querySelectorAll('button.flex.h-10.items-center');
                for (const btn of allBtns) {
                    if (btn.offsetParent === null) continue;
                    const text = btn.innerText.trim();
                    if (text.includes('\u0623\u062e\u062a\u0631') || text.includes('\u0627\u062e\u062a\u0631') || text.includes('\u0627\u062e\u062a\u064a\u0627\u0631')) {
                        results.push({ text: text, rect: btn.getBoundingClientRect() });
                    }
                }
            }
            return results;
        }""")
        if placeholder_btns:
            for pb in placeholder_btns:
                try:
                    rect = pb.get('rect', {})
                    if rect:
                        page.mouse.click(rect['x'] + rect['width']/2, rect['y'] + rect['height']/2)
                        time.sleep(0.8)
                        opt_text = page.evaluate("""() => {
                            const options = document.querySelectorAll('[role="option"], [data-radix-collection-item]');
                            const visible = Array.from(options).filter(o => o.offsetParent !== null);
                            if (visible.length > 0) {
                                let startIdx = 0;
                                const firstText = visible[0].innerText.trim();
                                if (firstText.includes('\u0623\u062e\u062a\u0631') || firstText.includes('\u0627\u062e\u062a\u0631') || firstText === '') startIdx = 1;
                                if (visible.length > startIdx) {
                                    const idx = startIdx + Math.floor(Math.random() * (visible.length - startIdx));
                                    visible[idx].click();
                                    return visible[idx].innerText.trim().substring(0, 30);
                                }
                            }
                            return null;
                        }""")
                        if opt_text:
                            filled += 1
                            print(f"    [refill] React dropdown: '{opt_text}'", flush=True)
                        else:
                            try: page.keyboard.press('Escape')
                            except: pass
                        time.sleep(0.3)
                except:
                    try: page.keyboard.press('Escape')
                    except: pass
    except:
        pass
    
    # Handle Shadcn checkbox buttons (use Playwright click for React sync)
    try:
        peer_btns = page.locator('button.peer')
        for i in range(peer_btns.count()):
            try:
                btn = peer_btns.nth(i)
                if btn.is_visible():
                    state = btn.get_attribute('data-state') or btn.get_attribute('aria-checked') or ''
                    if state != 'checked' and state != 'true':
                        btn.click()
                        time.sleep(0.3)
            except:
                pass
        role_cbs = page.locator('button[role="checkbox"]')
        for i in range(role_cbs.count()):
            try:
                btn = role_cbs.nth(i)
                if btn.is_visible():
                    state = btn.get_attribute('data-state') or btn.get_attribute('aria-checked') or ''
                    if state != 'checked' and state != 'true':
                        btn.click()
                        time.sleep(0.3)
            except:
                pass
    except:
        pass
    
    return filled


def fill_form_dynamically(page):
    """Dynamically detect and fill ALL form fields on the current page"""
    print("  📝 Dynamic form detection starting...", flush=True)
    
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
    
    # ===== STEP 1: Discover and fill all INPUT fields =====
    try:
        field_info = page.evaluate("""() => {
            const fields = [];
            const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"])');
            
            for (const inp of inputs) {
                if (inp.offsetParent === null) continue; // skip hidden
                
                const ph = inp.getAttribute('placeholder') || '';
                const name = inp.getAttribute('name') || '';
                const id = inp.getAttribute('id') || '';
                const type = inp.getAttribute('type') || 'text';
                const ac = inp.getAttribute('autocomplete') || '';
                const aria = inp.getAttribute('aria-label') || '';
                const maxlen = inp.getAttribute('maxlength') || '';
                
                // Find associated label
                let labelText = '';
                if (id) {
                    const lbl = document.querySelector('label[for="' + id + '"]');
                    if (lbl) labelText = lbl.innerText.trim();
                }
                if (!labelText) {
                    // Check parent/previous sibling for label
                    let el = inp.previousElementSibling;
                    while (el) {
                        if (el.tagName === 'LABEL' || el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'H6') {
                            labelText = el.innerText.trim();
                            break;
                        }
                        el = el.previousElementSibling;
                    }
                    if (!labelText) {
                        const parent = inp.closest('.mb-4, .mb-3, .mb-2, .form-group, .field, [class*="form"], [class*="field"]');
                        if (parent) {
                            const lbl = parent.querySelector('label, .label, h6, h5');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                    }
                    if (!labelText) {
                        const parent = inp.parentElement;
                        if (parent) {
                            const lbl = parent.querySelector('label');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                    }
                }
                
                fields.push({
                    index: fields.length,
                    placeholder: ph,
                    name: name,
                    id: id,
                    type: type,
                    autocomplete: ac,
                    ariaLabel: aria,
                    label: labelText,
                    maxlength: maxlen,
                    selector: id ? '#' + CSS.escape(id) : (name ? 'input[name="' + name + '"]' : null),
                    value: inp.value || ''
                });
            }
            return fields;
        }""")
        
        if field_info:
            print(f"  🔍 Found {len(field_info)} input fields", flush=True)
            
            for field in field_info:
                # Build clues string from all attributes
                clues = f"{field['placeholder']} {field['label']} {field['name']} {field['id']} {field['autocomplete']} {field['ariaLabel']} type:{field['type']}"
                
                field_type = classify_input_field(clues)
                
                if field_type == 'unknown':
                    # Try maxlength-based detection
                    maxlen = field.get('maxlength', '')
                    if maxlen == '10' and not field.get('value'):
                        field_type = 'national_id'
                    elif maxlen == '4' and not field.get('value'):
                        field_type = 'plate_number'
                    else:
                        # Check if it looks like a date field
                        all_clues = f"{field['placeholder']} {field['label']} {field['name']} {field['id']}"
                        if any(w in all_clues for w in ['commissioner', 'مفوض']):
                            field_type = 'date_of_birth'
                        elif any(w in all_clues for w in ['\u062a\u0627\u0631\u064a\u062e', 'date', '\u0645\u0648\u0639\u062f']):
                            field_type = 'inspection_date'
                        elif field.get('type') == 'date':
                            field_type = 'inspection_date'
                        else:
                            print(f"    Unknown field: ph='{field['placeholder'][:30]}' label='{field['label'][:30]}' name='{field['name']}' id='{field['id']}'", flush=True)
                            # Try to fill unknown fields with a generic value based on type
                            if field.get('type') == 'number':
                                value = str(random.randint(1, 100))
                            elif field.get('type') == 'email':
                                field_type = 'email'
                            elif field.get('type') == 'tel':
                                field_type = 'phone'
                            else:
                                continue
                
                value = get_field_value(field_type, data)
                if not value:
                    continue
                
                # Skip if already has a value (but NOT date_of_birth - MUI defaults to today)
                if field.get('value') and len(field['value']) > 2:
                    if field_type == 'date_of_birth':
                        pass  # Always overwrite birth dates (MUI picker defaults to today)
                    else:
                        print(f"    \u23ed\ufe0f {field_type}: already has value '{field['value'][:20]}'", flush=True)
                        continue
                
                # Fill the field
                try:
                    selector = field.get('selector')
                    if selector:
                        el = page.locator(selector).first
                    else:
                        el = page.locator(f'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"]):visible').nth(field['index'])
                    
                    if el.is_visible():
                        if field.get('type') == 'date':
                            # Date inputs: focus, clear, fill, then dispatch
                            el.focus()
                            el.fill(value)
                            el.evaluate("""(el) => {
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""")
                        else:
                            # Text inputs: click, select all, type char-by-char (most human-like)
                            el.click()
                            time.sleep(random.uniform(0.1, 0.3))
                            el.press('Control+a')  # Select all existing text
                            time.sleep(0.1)
                            el.type(value, delay=random.randint(20, 50))  # Type char by char
                        el.press('Tab')  # Trigger blur
                        time.sleep(random.uniform(0.2, 0.5))
                        filled += 1
                        print(f"    \u2705 {field_type}: {value[:30]}", flush=True)
                except Exception as e:
                    print(f"    ❌ {field_type}: {str(e)[:60]}", flush=True)
                
                time.sleep(random.uniform(0.2, 0.5))
    
    except Exception as e:
        print(f"  ❌ Input detection error: {str(e)[:100]}", flush=True)
    
    # ===== STEP 2: Handle SELECT dropdowns =====
    try:
        select_info = page.evaluate("""() => {
            const selects = [];
            const allSelects = document.querySelectorAll('select');
            
            for (const sel of allSelects) {
                if (sel.offsetParent === null) continue; // skip hidden
                
                const name = sel.getAttribute('name') || '';
                const id = sel.getAttribute('id') || '';
                const aria = sel.getAttribute('aria-label') || '';
                
                // Find label
                let labelText = '';
                if (id) {
                    const lbl = document.querySelector('label[for="' + id + '"]');
                    if (lbl) labelText = lbl.innerText.trim();
                }
                if (!labelText) {
                    let el = sel.previousElementSibling;
                    while (el) {
                        if (el.tagName === 'LABEL' || el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'H6') {
                            labelText = el.innerText.trim();
                            break;
                        }
                        el = el.previousElementSibling;
                    }
                    if (!labelText) {
                        const parent = sel.closest('.mb-4, .mb-3, .mb-2, .form-group, .field, [class*="form"], [class*="field"]');
                        if (parent) {
                            const lbl = parent.querySelector('label, .label, h6, h5');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                    }
                    if (!labelText) {
                        const parent = sel.parentElement;
                        if (parent) {
                            const lbl = parent.querySelector('label');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                    }
                }
                
                // Get options
                const opts = Array.from(sel.options).map(o => ({
                    value: o.value,
                    text: o.text.trim(),
                    selected: o.selected
                }));
                
                // Check if it's a plate letter select (has Arabic letter options like "أ - A")
                const isPlateLetters = opts.some(o => o.text.includes(' - ') && o.text.length < 10);
                
                selects.push({
                    index: selects.length,
                    name: name,
                    id: id,
                    ariaLabel: aria,
                    label: labelText,
                    currentValue: sel.value,
                    options: opts,
                    isPlateLetters: isPlateLetters,
                    selector: id ? '#' + CSS.escape(id) : (name ? 'select[name="' + name + '"]' : null)
                });
            }
            return selects;
        }""")
        
        if select_info:
            print(f"  🔍 Found {len(select_info)} select dropdowns", flush=True)
            
            plate_letter_count = 0
            
            for sel in select_info:
                # Handle plate letter selects
                if sel.get('isPlateLetters') and plate_letter_count < 3:
                    try:
                        valid_opts = [o for o in sel['options'] if o['value'] and o['value'] not in ('', '-')]
                        if valid_opts:
                            choice = random.choice(valid_opts)
                            sel_el = page.locator('select:visible').nth(sel['index'])
                            sel_el.select_option(value=choice['value'])
                            # Trigger React onChange
                            sel_el.evaluate("""(el) => {
                                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                                nativeSetter.call(el, el.value);
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                            }""")
                            plate_letter_count += 1
                            filled += 1
                            print(f"    ✅ حرف لوحة {plate_letter_count}: {choice['text'][:10]}", flush=True)
                    except:
                        pass
                    continue
                
                # Classify the select
                clues = f"{sel['label']} {sel['name']} {sel['id']} {sel['ariaLabel']}"
                field_type, preferred = classify_select_field(clues)
                
                # Skip if already has a valid value
                if sel.get('currentValue') and sel['currentValue'] not in ('', '-', '0'):
                    # Check if it's not just the default/placeholder option
                    current_opt = next((o for o in sel['options'] if o['value'] == sel['currentValue']), None)
                    if current_opt:
                        opt_text = current_opt.get('text', '')
                        placeholder_words = ['\u0627\u062e\u062a\u0631', '\u0627\u062e\u062a\u064a\u0627\u0631', 'Select', 'Choose', '--', '---']
                        is_placeholder = any(pw in opt_text for pw in placeholder_words)
                        if not is_placeholder and len(opt_text) > 0:
                            print(f"    \u23ed\ufe0f {field_type}: already selected '{opt_text[:20]}'", flush=True)
                            continue
                
                valid_opts = [o for o in sel['options'] if o['value'] and o['value'] not in ('', '-') and 'اختر' not in o.get('text', '')]
                
                if not valid_opts:
                    continue
                
                # Choose option
                chosen = None
                if preferred:
                    # Try to find preferred option
                    for opt in valid_opts:
                        if preferred in opt.get('text', '') or preferred in opt.get('value', ''):
                            chosen = opt
                            break
                
                if not chosen:
                    chosen = random.choice(valid_opts)
                
                try:
                    sel_el = page.locator('select:visible').nth(sel['index'])
                    sel_el.select_option(value=chosen['value'])
                    # Trigger React onChange
                    sel_el.evaluate("""(el) => {
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                        nativeSetter.call(el, el.value);
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                    }""")
                    filled += 1
                    print(f"    \u2705 {field_type}: {chosen['text'][:30]}", flush=True)
                    
                    # Wait for dependent dropdowns to load (region -> center)
                    if field_type in ('region', 'country', 'nationality'):
                        time.sleep(random.uniform(2, 3))
                        # Re-scan selects to find newly loaded dependent dropdowns (e.g., center)
                        try:
                            new_selects = page.evaluate("""() => {
                                const selects = [];
                                const allSelects = document.querySelectorAll('select');
                                for (const sel of allSelects) {
                                    if (sel.offsetParent === null) continue;
                                    const name = sel.getAttribute('name') || '';
                                    const id = sel.getAttribute('id') || '';
                                    const aria = sel.getAttribute('aria-label') || '';
                                    let labelText = '';
                                    if (id) {
                                        const lbl = document.querySelector('label[for="' + id + '"]');
                                        if (lbl) labelText = lbl.innerText.trim();
                                    }
                                    if (!labelText) {
                                        let el = sel.previousElementSibling;
                                        while (el) {
                                            if (el.tagName === 'LABEL' || el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'H6') {
                                                labelText = el.innerText.trim();
                                                break;
                                            }
                                            el = el.previousElementSibling;
                                        }
                                        if (!labelText) {
                                            const parent = sel.parentElement;
                                            if (parent) {
                                                const lbl = parent.querySelector('label');
                                                if (lbl) labelText = lbl.innerText.trim();
                                            }
                                        }
                                    }
                                    const opts = Array.from(sel.options).map(o => ({
                                        value: o.value,
                                        text: o.text.trim(),
                                        selected: o.selected
                                    }));
                                    const hasValue = sel.value && sel.value !== '' && sel.value !== '-' && sel.value !== '0';
                                    selects.push({
                                        name: name,
                                        id: id,
                                        ariaLabel: aria,
                                        label: labelText,
                                        currentValue: sel.value,
                                        options: opts,
                                        hasValue: hasValue,
                                        visibleIndex: selects.length
                                    });
                                }
                                return selects;
                            }""")
                            
                            # Find and fill any new empty selects (like center)
                            for ns in new_selects:
                                if ns.get('hasValue'):
                                    # Check if it's a placeholder value
                                    current_opt = next((o for o in ns['options'] if o['value'] == ns['currentValue']), None)
                                    if current_opt:
                                        opt_text = current_opt.get('text', '')
                                        if not any(pw in opt_text for pw in ['\u0627\u062e\u062a\u0631', '\u0627\u062e\u062a\u064a\u0627\u0631', 'Select', 'Choose']):
                                            continue
                                
                                ns_clues = f"{ns['label']} {ns['name']} {ns['id']} {ns['ariaLabel']}"
                                ns_type, ns_pref = classify_select_field(ns_clues)
                                
                                # Only fill center/branch type selects or unknown ones with options
                                ns_valid = [o for o in ns['options'] if o['value'] and o['value'] not in ('', '-') and '\u0627\u062e\u062a\u0631' not in o.get('text', '')]
                                if not ns_valid:
                                    continue
                                
                                ns_chosen = random.choice(ns_valid)
                                try:
                                    dep_sel = page.locator('select:visible').nth(ns['visibleIndex'])
                                    dep_sel.select_option(value=ns_chosen['value'])
                                    dep_sel.evaluate("""(el) => {
                                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                                        nativeSetter.call(el, el.value);
                                        el.dispatchEvent(new Event('change', { bubbles: true }));
                                        el.dispatchEvent(new Event('input', { bubbles: true }));
                                    }""")
                                    filled += 1
                                    print(f"    ✅ [dependent] {ns_type}: {ns_chosen['text'][:30]}", flush=True)
                                    time.sleep(random.uniform(0.5, 1))
                                except Exception as de:
                                    print(f"    ❌ [dependent] {ns_type}: {str(de)[:60]}", flush=True)
                        except Exception as re_err:
                            print(f"    ⚠️ Re-scan error: {str(re_err)[:60]}", flush=True)
                    else:
                        time.sleep(random.uniform(0.3, 0.6))
                    
                except Exception as e:
                    print(f"    ❌ {field_type}: {str(e)[:60]}", flush=True)
    
    except Exception as e:
        print(f"  ❌ Select detection error: {str(e)[:100]}", flush=True)
    
    # ===== STEP 2b: Handle React custom dropdown buttons (Shadcn/Radix Select) =====
    # Some sites use custom React dropdowns (buttons) alongside hidden native <select> elements.
    # The native select may have a value but React state is NOT synced, so we click the button UI.
    try:
        # Find all custom select trigger buttons that still show placeholder text
        placeholder_buttons = page.evaluate("""() => {
            const results = [];
            const buttons = document.querySelectorAll('button[role="combobox"], button[data-state], button[aria-expanded]');
            for (const btn of buttons) {
                if (btn.offsetParent === null) continue;
                const text = btn.innerText.trim();
                // Check if button shows placeholder (أختر = Choose)
                if (text.includes('أختر') || text.includes('اختر') || text.includes('اختيار') || text === '') {
                    results.push({
                        text: text,
                        index: results.length,
                        rect: btn.getBoundingClientRect()
                    });
                }
            }
            // Also find by class pattern used in Shadcn UI selects
            if (results.length === 0) {
                const allBtns = document.querySelectorAll('button.flex.h-10.items-center');
                for (const btn of allBtns) {
                    if (btn.offsetParent === null) continue;
                    const text = btn.innerText.trim();
                    if (text.includes('أختر') || text.includes('اختر') || text.includes('اختيار')) {
                        results.push({
                            text: text,
                            index: results.length,
                            rect: btn.getBoundingClientRect()
                        });
                    }
                }
            }
            return results;
        }""")
        
        if placeholder_buttons:
            print(f"  🔧 Found {len(placeholder_buttons)} React custom dropdowns with placeholder", flush=True)
            for pb in placeholder_buttons:
                try:
                    # Click the placeholder button to open dropdown
                    btn_text = pb['text']
                    btn_locator = None
                    
                    # Try to find by exact text
                    if btn_text:
                        candidates = page.locator(f'button:has-text("{btn_text}")')
                        for ci in range(candidates.count()):
                            c = candidates.nth(ci)
                            if c.is_visible():
                                inner = c.inner_text().strip()
                                if inner == btn_text or 'أختر' in inner or 'اختر' in inner:
                                    btn_locator = c
                                    break
                    
                    if not btn_locator:
                        # Fallback: click by coordinates
                        rect = pb.get('rect', {})
                        if rect:
                            page.mouse.click(rect['x'] + rect['width']/2, rect['y'] + rect['height']/2)
                            time.sleep(0.5)
                        else:
                            continue
                    else:
                        btn_locator.click()
                        time.sleep(0.5)
                    
                    # Wait for dropdown options to appear
                    time.sleep(0.5)
                    
                    # Click a random option from the dropdown
                    options_clicked = page.evaluate("""() => {
                        // Shadcn/Radix UI dropdown options
                        const options = document.querySelectorAll('[role="option"], [data-radix-collection-item], [cmdk-item]');
                        const visible = Array.from(options).filter(o => o.offsetParent !== null);
                        if (visible.length > 0) {
                            // Skip first if it's a placeholder
                            let startIdx = 0;
                            const firstText = visible[0].innerText.trim();
                            if (firstText.includes('أختر') || firstText.includes('اختر') || firstText === '') startIdx = 1;
                            if (visible.length > startIdx) {
                                const idx = startIdx + Math.floor(Math.random() * (visible.length - startIdx));
                                visible[idx].click();
                                return visible[idx].innerText.trim().substring(0, 30);
                            }
                        }
                        // Fallback: try listbox items
                        const listItems = document.querySelectorAll('[role="listbox"] > *, .select-option, [class*="option"]');
                        const visItems = Array.from(listItems).filter(o => o.offsetParent !== null);
                        if (visItems.length > 0) {
                            const idx = Math.floor(Math.random() * visItems.length);
                            visItems[idx].click();
                            return visItems[idx].innerText.trim().substring(0, 30);
                        }
                        return null;
                    }""")
                    
                    if options_clicked:
                        filled += 1
                        print(f"    ✅ React dropdown: selected '{options_clicked}'", flush=True)
                    else:
                        # Try pressing Escape to close if nothing was selected
                        try:
                            page.keyboard.press('Escape')
                        except:
                            pass
                        print(f"    ⚠️ React dropdown: no options found for '{btn_text}'", flush=True)
                    
                    time.sleep(random.uniform(0.3, 0.6))
                    
                except Exception as rde:
                    print(f"    ❌ React dropdown error: {str(rde)[:60]}", flush=True)
                    try:
                        page.keyboard.press('Escape')
                    except:
                        pass
    except Exception as e:
        print(f"  ⚠️ React dropdown scan error: {str(e)[:80]}", flush=True)
    
    # ===== STEP 2c: Handle Shadcn/Radix checkbox buttons =====
    # These are <button> elements with role="checkbox" or class containing "peer" + "rounded"
    try:
        # Use Playwright click (not JS click) for better React state sync
        peer_btns = page.locator('button.peer')
        peer_count = peer_btns.count()
        for i in range(peer_count):
            try:
                btn = peer_btns.nth(i)
                if btn.is_visible():
                    state = btn.get_attribute('data-state') or btn.get_attribute('aria-checked') or ''
                    if state != 'checked' and state != 'true':
                        btn.click()
                        time.sleep(0.3)
                        print(f"    \u2705 Clicked peer checkbox #{i+1}", flush=True)
            except:
                pass
        
        # Also handle role=checkbox buttons
        role_cbs = page.locator('button[role="checkbox"]')
        for i in range(role_cbs.count()):
            try:
                btn = role_cbs.nth(i)
                if btn.is_visible():
                    state = btn.get_attribute('data-state') or btn.get_attribute('aria-checked') or ''
                    if state != 'checked' and state != 'true':
                        btn.click()
                        time.sleep(0.3)
                        print(f"    \u2705 Clicked role=checkbox #{i+1}", flush=True)
            except:
                pass
        
        print(f"    \u2705 Shadcn checkboxes handled ({peer_count} peer btns)", flush=True)
    except Exception as cbe:
        print(f"    \u26a0\ufe0f Shadcn checkbox error: {str(cbe)[:60]}", flush=True)
    
    # ===== STEP 3: Handle radio buttons and checkboxes =====
    try:
        page.evaluate("""() => {
            // Click first visible radio in each group
            const groups = {};
            const radios = document.querySelectorAll('input[type="radio"]');
            for (const r of radios) {
                if (r.offsetParent === null) continue;
                const name = r.getAttribute('name') || 'default';
                if (!groups[name]) {
                    groups[name] = [];
                }
                groups[name].push(r);
            }
            for (const name in groups) {
                const checked = groups[name].find(r => r.checked);
                if (!checked && groups[name].length > 0) {
                    const choice = groups[name][Math.floor(Math.random() * groups[name].length)];
                    choice.click();
                    choice.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
            
            // Check unchecked required checkboxes (terms, agreements)
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (const cb of checkboxes) {
                if (cb.offsetParent === null) continue;
                if (!cb.checked) {
                    cb.click();
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }""")
        print(f"    ✅ Radio/Checkbox handled", flush=True)
    except:
        pass
    
    # ===== STEP 4: Click specific buttons like "تحمل رخصة سير" =====
    for btn_text in ['تحمل رخصة سير', 'لا تحمل رخصة سير']:
        try:
            btn = page.get_by_text(btn_text)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                filled += 1
                print(f"    ✅ Clicked: {btn_text}", flush=True)
                time.sleep(random.uniform(0.5, 1))
                break
        except:
            continue
    
    # ===== STEP 5: Scroll down and fill ALL remaining empty fields =====
    try:
        page.evaluate("window.scrollTo(0, 600)")
        time.sleep(1)
    except:
        pass
    
    # ===== STEP 6: Multiple passes to fill dependent fields =====
    # After selecting region/area, new selects appear (like inspection center)
    # We need to keep filling until nothing is empty
    for pass_num in range(4):
        time.sleep(1.5)
        extra = fill_all_empty_fields(page, data)
        if extra > 0:
            print(f"    Pass {pass_num+2}: filled {extra} more fields", flush=True)
            filled += extra
        else:
            break
    
    # ===== STEP 7: Final checkbox/agreement check =====
    # Some checkboxes (like delegation terms) only appear after delegation is enabled
    # Re-check ALL checkboxes and check any unchecked ones
    try:
        page.evaluate("""() => {
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (const cb of checkboxes) {
                if (cb.offsetParent === null) continue;
                if (!cb.checked) {
                    cb.click();
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                    cb.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
        }""")
        print(f"    \u2705 Final checkbox re-check done", flush=True)
    except:
        pass
    
    # Also try clicking any agreement/terms text that might be a clickable label
    for agree_text in ['أوافق', 'الموافقة', 'شروط التفويض', 'الشروط والأحكام']:
        try:
            el = page.get_by_text(agree_text)
            if el.count() > 0 and el.first.is_visible():
                # Check if there's a nearby unchecked checkbox
                parent = el.first.locator('xpath=ancestor::label | xpath=preceding-sibling::input[@type="checkbox"]')
                if parent.count() > 0:
                    parent.first.click()
                    print(f"    \u2705 Clicked agreement: {agree_text}", flush=True)
                    time.sleep(0.3)
        except:
            pass
    
    # ===== STEP 7b: Handle attendance confirmation checkbox =====
    # Some sites have a confirmation about attendance that uses non-standard checkbox elements
    try:
        page.evaluate("""() => {
            // Find any element containing attendance confirmation text
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                const text = el.innerText || el.textContent || '';
                if (text.includes('الحضور على الموعد') || text.includes('الحضور علي الموعد')) {
                    // Try to find and click a checkbox near this element
                    const parent = el.closest('label, div, span');
                    if (parent) {
                        const cb = parent.querySelector('input[type="checkbox"]');
                        if (cb && !cb.checked) {
                            cb.click();
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                            cb.dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                        // Maybe the parent itself is clickable
                        const clickable = parent.querySelector('[role="checkbox"], .checkbox, .MuiCheckbox-root, svg');
                        if (clickable) {
                            clickable.click();
                            break;
                        }
                    }
                    // Try clicking the element itself or its parent
                    el.click();
                    break;
                }
            }
            // Also try: find any unchecked checkbox near red error text
            const errors = document.querySelectorAll('.text-red-500, .text-red-600');
            for (const err of errors) {
                const parent = err.closest('div, label, fieldset');
                if (parent) {
                    const cb = parent.querySelector('input[type="checkbox"]:not(:checked)');
                    if (cb) {
                        cb.click();
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    const muiCb = parent.querySelector('[role="checkbox"], .MuiCheckbox-root');
                    if (muiCb) {
                        muiCb.click();
                    }
                }
            }
        }""")
        print(f"    \u2705 Attendance confirmation check done", flush=True)
    except:
        pass
    
    # ===== STEP 7c: Fix MUI DatePicker for commissioner-date =====
    # MUI DatePicker inputs don't accept regular typing - use JS to set value directly
    try:
        birth_year = random.randint(1970, 2000)
        birth_month = f"{random.randint(1, 12):02d}"
        birth_day = f"{random.randint(1, 28):02d}"
        birth_date = f"{birth_month}/{birth_day}/{birth_year}"
        
        date_fixed = page.evaluate("""(birthDate) => {
            const results = [];
            // Find commissioner-date input
            const dateInputs = document.querySelectorAll('input[name*="commissioner-date"], input[name*="commissioner_date"]');
            for (const inp of dateInputs) {
                if (inp.offsetParent === null) continue;
                const currentVal = inp.value;
                if (currentVal.includes('2026') || currentVal.includes('2025') || currentVal.includes('2024')) {
                    // Use React's nativeInputValueSetter to bypass read-only
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(inp, birthDate);
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    inp.dispatchEvent(new Event('blur', { bubbles: true }));
                    
                    // Also try React fiber approach
                    const key = Object.keys(inp).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                    if (key) {
                        const fiber = inp[key];
                        if (fiber && fiber.memoizedProps && fiber.memoizedProps.onChange) {
                            fiber.memoizedProps.onChange({ target: { value: birthDate } });
                        }
                    }
                    
                    results.push({ old: currentVal, new: inp.value, birthDate: birthDate });
                }
            }
            return results;
        }""", birth_date)
        
        if date_fixed and len(date_fixed) > 0:
            for df in date_fixed:
                print(f"    \u2705 Commissioner date: {df.get('old','')} -> {df.get('new','')} (target: {birth_date})", flush=True)
                filled += 1
        else:
            print(f"    \u26a0\ufe0f No commissioner-date inputs found to fix", flush=True)
    except Exception as de:
        print(f"    \u26a0\ufe0f Commissioner date error: {str(de)[:60]}", flush=True)
    
    # Scroll down to make sure everything is visible
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
    except:
        pass
    
    print(f"  \U0001f4ca Total fields filled: {filled}", flush=True)
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
    for text in ['بطاقة ائتمان', 'مدى', 'بطاقة ائتمان / مدى', 'Visa', 'MasterCard', 'بطاقة', 'Credit Card']:
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
    for text in ['متابعة الدفع', 'متابعة', 'استمرار', 'Continue', 'Proceed', 'ادفع']:
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
            
            # Debug: dump all input attributes
            for dbg_i, dbg_inp in enumerate(inputs):
                try:
                    dbg_ph = (dbg_inp.get_attribute('placeholder') or '')[:30]
                    dbg_name = (dbg_inp.get_attribute('name') or '')[:30]
                    dbg_id = (dbg_inp.get_attribute('id') or '')[:30]
                    dbg_type = (dbg_inp.get_attribute('type') or 'text')[:15]
                    dbg_ac = (dbg_inp.get_attribute('autocomplete') or '')[:20]
                    dbg_aria = (dbg_inp.get_attribute('aria-label') or '')[:30]
                    dbg_val = (dbg_inp.input_value() or '')[:15]
                    print(f"    🔍 INPUT[{dbg_i}]: type={dbg_type} name={dbg_name} id={dbg_id} ph={dbg_ph} ac={dbg_ac} aria={dbg_aria} val={dbg_val}", flush=True)
                except:
                    pass
            
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
                    
                    if any(kw in clues for kw in ['card number', 'cardnumber', 'cc-number', 'pan', '1234', 'رقم البطاقة', 'card_number', 'cardno']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill('')
                        for ch in card_num:
                            inp.type(ch, delay=random.randint(40, 100))
                        filled += 1
                        print(f"    ✅ رقم البطاقة: {card_num[:4]}****{card_num[-4:]}", flush=True)
                    
                    elif any(kw in clues for kw in ['holder', 'cardholder', 'name on', 'cc-name', 'حامل', 'الاسم كما', 'card_holder', 'cardname', 'nameoncard', 'name_on_card']):
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
                                    sel.evaluate("""(el) => { const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(el, el.value); el.dispatchEvent(new Event('change', { bubbles: true })); }""")
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
                                    sel.evaluate("""(el) => { const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(el, el.value); el.dispatchEvent(new Event('change', { bubbles: true })); }""")
                                    filled += 1
                                    year_done = True
                                    print(f"    ✅ سنة الانتهاء: {exp_year}", flush=True)
                                    break
                            if not year_done:
                                valid_years = [o for o in options if (o.get_attribute('value') or '').strip() and (o.get_attribute('value') or '').strip() not in ['', '-', '0']]
                                if valid_years:
                                    sel.select_option(value=valid_years[min(2, len(valid_years)-1)].get_attribute('value'))
                                    sel.evaluate("""(el) => { const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(el, el.value); el.dispatchEvent(new Event('change', { bubbles: true })); }""")
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
    
    # Handle MUI Select dropdowns for expiry month/year
    print(f"    🔍 Starting MUI Select detection for expiry month/year...", flush=True)
    
    try:
        month_done = False
        year_done = False
        
        # APPROACH 1: Use JavaScript to directly set values via React internals
        # This is the most reliable approach for MUI Select with React Hook Form
        try:
            js_select_result = page.evaluate("""(data) => {
                const results = [];
                
                // Find all MUI Select elements (they use div[role=combobox] or have MuiSelect class)
                const selects = document.querySelectorAll('[role="combobox"], .MuiSelect-select, [aria-haspopup="listbox"]');
                results.push('Found ' + selects.length + ' MUI select elements');
                
                for (let i = 0; i < selects.length; i++) {
                    const sel = selects[i];
                    const text = sel.textContent?.trim() || '';
                    const cls = sel.className || '';
                    results.push('SEL[' + i + ']: text="' + text + '" class=' + cls.substring(0, 60));
                }
                
                return results;
            }""", card_data)
            if js_select_result:
                for r in js_select_result:
                    print(f"    🔍 {r}", flush=True)
        except Exception as dbg_e:
            print(f"    ⚠️ Debug dump error: {str(dbg_e)[:60]}", flush=True)
        
        # APPROACH 1A: Click MUI Select triggers and pick correct month/year values
        try:
            # MUI Select uses div[role="combobox"] NOT button[role="combobox"]
            mui_triggers = page.locator('[role="combobox"]:visible').all()
            print(f"    🔍 Found {len(mui_triggers)} combobox elements (MUI)", flush=True)
            
            # First pass: identify which trigger is month and which is year by TEXT
            month_trigger = None
            year_trigger = None
            for i, trigger in enumerate(mui_triggers):
                try:
                    if not trigger.is_visible():
                        continue
                    btn_text = trigger.inner_text().strip()
                    tag_name = trigger.evaluate('el => el.tagName')
                    print(f"    🔍 MUI Trigger {i}: <{tag_name}> text='{btn_text}'", flush=True)
                    
                    if tag_name.upper() == 'INPUT':
                        continue
                    
                    # Identify by text - "شهر" = month, "سنة" = year
                    if any(kw in btn_text for kw in ['شهر', 'الشهر', 'Month', 'MM']):
                        month_trigger = trigger
                        print(f"    🔍 Identified trigger {i} as MONTH", flush=True)
                    elif any(kw in btn_text for kw in ['سنة', 'السنة', 'Year', 'YY']):
                        year_trigger = trigger
                        print(f"    🔍 Identified trigger {i} as YEAR", flush=True)
                    else:
                        # If text is a number, check if it looks like month (1-12) or year (24-35)
                        try:
                            num = int(btn_text)
                            if 1 <= num <= 12:
                                month_trigger = trigger
                            elif 20 <= num <= 99:
                                year_trigger = trigger
                        except:
                            pass
                except:
                    continue
            
            # If we couldn't identify by text, assign by count: fewer options = month (12), more = year
            if not month_trigger and not year_trigger and len(mui_triggers) >= 2:
                # We'll identify after clicking by option count
                month_trigger = mui_triggers[0]
                year_trigger = mui_triggers[1]
                print(f"    🔍 Assigned triggers by position (will verify by options)", flush=True)
            
            # Handle MONTH trigger
            if month_trigger and not month_done:
                month_trigger.click()
                time.sleep(1.5)
                options = page.locator('[role="option"]:visible, li.MuiMenuItem-root:visible').all()
                opt_texts = [o.inner_text().strip() for o in options]
                print(f"    🔍 Month dropdown options ({len(options)}): {opt_texts[:15]}", flush=True)
                
                if options:
                    # Verify this is actually month options (should have values 01-12 or 1-12)
                    for opt in options:
                        ot = opt.inner_text().strip()
                        if ot == exp_month or ot == str(int(exp_month)) or ot == exp_month.lstrip('0'):
                            opt.click()
                            month_done = True
                            filled += 1
                            print(f"    ✅ شهر الانتهاء: {ot} (exact match)", flush=True)
                            break
                    if not month_done:
                        # Close and try - maybe this was year dropdown
                        page.keyboard.press('Escape')
                        print(f"    ⚠️ Could not match month {exp_month} in options", flush=True)
                else:
                    page.keyboard.press('Escape')
                time.sleep(0.5)
            
            # Handle YEAR trigger
            if year_trigger and not year_done:
                year_trigger.click()
                time.sleep(1.5)
                options = page.locator('[role="option"]:visible, li.MuiMenuItem-root:visible').all()
                opt_texts = [o.inner_text().strip() for o in options]
                print(f"    🔍 Year dropdown options ({len(options)}): {opt_texts[:15]}", flush=True)
                
                if options:
                    exp_year_short = exp_year[-2:] if len(exp_year) == 4 else exp_year
                    exp_year_int = str(int(exp_year_short)) if exp_year_short.isdigit() else exp_year_short
                    
                    for opt in options:
                        ot = opt.inner_text().strip()
                        if ot == exp_year or ot == exp_year_short or ot == exp_year_int:
                            opt.click()
                            year_done = True
                            filled += 1
                            print(f"    ✅ سنة الانتهاء: {ot} (exact match)", flush=True)
                            break
                    if not year_done:
                        page.keyboard.press('Escape')
                        print(f"    ⚠️ Could not match year {exp_year} in options", flush=True)
                else:
                    page.keyboard.press('Escape')
                time.sleep(0.5)
            
            # If month still not done (maybe triggers were swapped), try the year_trigger for month
            if not month_done and year_trigger:
                print(f"    🔍 Retrying: maybe triggers are swapped...", flush=True)
                year_trigger.click()
                time.sleep(1.5)
                options = page.locator('[role="option"]:visible, li.MuiMenuItem-root:visible').all()
                opt_texts = [o.inner_text().strip() for o in options]
                print(f"    🔍 Swap-check options: {opt_texts[:15]}", flush=True)
                if options:
                    for opt in options:
                        ot = opt.inner_text().strip()
                        if ot == exp_month or ot == str(int(exp_month)) or ot == exp_month.lstrip('0'):
                            opt.click()
                            month_done = True
                            filled += 1
                            print(f"    ✅ شهر الانتهاء (swapped): {ot}", flush=True)
                            break
                    if not month_done:
                        page.keyboard.press('Escape')
                else:
                    page.keyboard.press('Escape')
                time.sleep(0.5)
            
            # If year still not done, try month_trigger for year
            if not year_done and month_trigger:
                month_trigger.click()
                time.sleep(1.5)
                options = page.locator('[role="option"]:visible, li.MuiMenuItem-root:visible').all()
                opt_texts = [o.inner_text().strip() for o in options]
                print(f"    🔍 Swap-check year options: {opt_texts[:15]}", flush=True)
                if options:
                    exp_year_short = exp_year[-2:] if len(exp_year) == 4 else exp_year
                    exp_year_int = str(int(exp_year_short)) if exp_year_short.isdigit() else exp_year_short
                    for opt in options:
                        ot = opt.inner_text().strip()
                        if ot == exp_year or ot == exp_year_short or ot == exp_year_int:
                            opt.click()
                            year_done = True
                            filled += 1
                            print(f"    ✅ سنة الانتهاء (swapped): {ot}", flush=True)
                            break
                    if not year_done:
                        page.keyboard.press('Escape')
                else:
                    page.keyboard.press('Escape')
                time.sleep(0.5)
                
        except Exception as e1:
            print(f"    ⚠️ MUI combobox search error: {str(e1)[:60]}", flush=True)
        
        # APPROACH 2: If MUI click approach failed, use JavaScript to directly manipulate React state
        if not month_done or not year_done:
            print(f"    🔍 Trying JS React state approach (month={month_done}, year={year_done})...", flush=True)
            try:
                js_result = page.evaluate("""(data) => {
                    const results = [];
                    
                    // Find all MUI Select elements by their rendered structure
                    // MUI Select renders: FormControl > Select > div.MuiSelect-select[role=combobox]
                    const comboboxes = document.querySelectorAll('[role="combobox"]');
                    results.push('JS: Found ' + comboboxes.length + ' comboboxes');
                    
                    // Try to find and click month/year selects
                    for (const cb of comboboxes) {
                        const text = cb.textContent?.trim() || '';
                        const parent = cb.closest('.MuiFormControl-root') || cb.parentElement;
                        results.push('JS combobox: text="' + text + '"');
                    }
                    
                    // Alternative: Find select elements by looking for MUI hidden inputs
                    const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
                    for (const inp of hiddenInputs) {
                        const name = inp.name || '';
                        if (name.includes('expiry') || name.includes('month') || name.includes('year')) {
                            results.push('Hidden input: name=' + name + ' value=' + inp.value);
                        }
                    }
                    
                    return results;
                }""", card_data)
                if js_result:
                    for r in js_result:
                        print(f"    🔍 {r}", flush=True)
            except:
                pass
        
        # APPROACH 3: If still not done, try clicking any div that looks like a select with "شهر" or "سنة"
        if not month_done or not year_done:
            print(f"    🔍 Trying text-based click approach...", flush=True)
            try:
                # Find elements containing "شهر" or "سنة" text
                if not month_done:
                    month_el = page.locator('div:has-text("شهر"):visible').last
                    if month_el.count() > 0:
                        # Click the MUI Select (it might be a parent div)
                        month_el.click()
                        time.sleep(1.5)
                        options = page.locator('[role="option"]:visible, li.MuiMenuItem-root:visible').all()
                        print(f"    🔍 Month options (text-based): {len(options)}", flush=True)
                        if options and len(options) >= 2:
                            # Skip first option if it's the placeholder
                            start = 1 if options[0].inner_text().strip() in ['شهر', '0', ''] else 0
                            for opt in options[start:]:
                                ot = opt.inner_text().strip()
                                if ot == exp_month or ot == str(int(exp_month)):
                                    opt.click()
                                    month_done = True
                                    filled += 1
                                    print(f"    ✅ شهر الانتهاء (text): {exp_month}", flush=True)
                                    break
                            if not month_done and len(options) > start:
                                options[start + random.randint(0, min(11, len(options)-start-1))].click()
                                month_done = True
                                filled += 1
                                print(f"    ✅ شهر الانتهاء (text fallback)", flush=True)
                        else:
                            try: page.keyboard.press('Escape')
                            except: pass
                        time.sleep(0.5)
                
                if not year_done:
                    year_el = page.locator('div:has-text("سنة"):visible').last
                    if year_el.count() > 0:
                        year_el.click()
                        time.sleep(1.5)
                        options = page.locator('[role="option"]:visible, li.MuiMenuItem-root:visible').all()
                        print(f"    🔍 Year options (text-based): {len(options)}", flush=True)
                        if options and len(options) >= 2:
                            start = 1 if options[0].inner_text().strip() in ['سنة', '0', ''] else 0
                            exp_year_short = exp_year[-2:] if len(exp_year) == 4 else exp_year
                            for opt in options[start:]:
                                ot = opt.inner_text().strip()
                                if ot == exp_year or ot == exp_year_short or ot == str(int(exp_year_short)):
                                    opt.click()
                                    year_done = True
                                    filled += 1
                                    print(f"    ✅ سنة الانتهاء (text): {ot}", flush=True)
                                    break
                            if not year_done and len(options) > start:
                                idx = min(start + 2, len(options) - 1)
                                options[idx].click()
                                year_done = True
                                filled += 1
                                print(f"    ✅ سنة الانتهاء (text fallback)", flush=True)
                        else:
                            try: page.keyboard.press('Escape')
                            except: pass
                        time.sleep(0.5)
            except Exception as e3:
                print(f"    ⚠️ Text-based approach error: {str(e3)[:60]}", flush=True)
        
        # APPROACH 4: Shadcn Select fallback (button[role=combobox] or data-slot)
        if not month_done or not year_done:
            print(f"    🔍 Trying Shadcn Select fallback...", flush=True)
            try:
                shadcn_triggers = page.locator('button[role="combobox"]:visible, [data-slot="select-trigger"]:visible').all()
                print(f"    🔍 Found {len(shadcn_triggers)} Shadcn triggers", flush=True)
                for i, trigger in enumerate(shadcn_triggers):
                    if month_done and year_done:
                        break
                    try:
                        btn_text = trigger.inner_text().strip()
                        print(f"    🔍 Shadcn trigger {i}: '{btn_text}'", flush=True)
                        
                        if not month_done:
                            trigger.click()
                            time.sleep(1)
                            options = page.locator('[role="option"]:visible').all()
                            if options and len(options) <= 12:
                                for opt in options:
                                    ot = opt.inner_text().strip()
                                    if ot == exp_month or ot == str(int(exp_month)):
                                        opt.click()
                                        month_done = True
                                        filled += 1
                                        print(f"    ✅ شهر الانتهاء (shadcn): {exp_month}", flush=True)
                                        break
                                if not month_done:
                                    options[random.randint(0, min(11, len(options)-1))].click()
                                    month_done = True
                                    filled += 1
                                    print(f"    ✅ شهر الانتهاء (shadcn fallback)", flush=True)
                            else:
                                page.keyboard.press('Escape')
                            time.sleep(0.5)
                        elif not year_done:
                            trigger.click()
                            time.sleep(1)
                            options = page.locator('[role="option"]:visible').all()
                            if options:
                                exp_year_short = exp_year[-2:] if len(exp_year) == 4 else exp_year
                                for opt in options:
                                    ot = opt.inner_text().strip()
                                    if ot == exp_year or ot == exp_year_short:
                                        opt.click()
                                        year_done = True
                                        filled += 1
                                        print(f"    ✅ سنة الانتهاء (shadcn): {ot}", flush=True)
                                        break
                                if not year_done:
                                    valid_opts = [o for o in options if o.inner_text().strip().isdigit()]
                                    if valid_opts:
                                        valid_opts[min(2, len(valid_opts)-1)].click()
                                        year_done = True
                                        filled += 1
                                        print(f"    ✅ سنة الانتهاء (shadcn fallback)", flush=True)
                            else:
                                page.keyboard.press('Escape')
                            time.sleep(0.5)
                    except:
                        try: page.keyboard.press('Escape')
                        except: pass
            except Exception as e4:
                print(f"    ⚠️ Shadcn fallback error: {str(e4)[:60]}", flush=True)
        
        if month_done:
            print(f"    ✅ Month selected", flush=True)
        else:
            print(f"    ⚠️ Month NOT selected", flush=True)
        if year_done:
            print(f"    ✅ Year selected", flush=True)
        else:
            print(f"    ⚠️ Year NOT selected", flush=True)
    except Exception as e:
        print(f"    ⚠️ Custom select error: {str(e)[:80]}", flush=True)
    
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
                    
                    if (text.includes('رقم البطاقة') || text.includes('Card Number')) { value = data.card_number; fieldName = 'card'; }
                    else if (text.includes('اسم حامل') || text.includes('حامل البطاقة') || text.includes('Cardholder') || text.includes('Name on Card') || text.includes('اسم على البطاقة')) { value = data.card_holder; fieldName = 'holder'; }
                    else if (text.includes('رمز الأمان') || text.includes('CVV') || text.includes('CVC')) { value = data.card_cvv; fieldName = 'cvv'; }
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
                'button:has-text("Pay Now")', 'button:has-text("Submit")',
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

def handle_next_pages(page, max_pages=8, data=None):
    """Handle multi-step form pages after initial registration"""
    retry_count = 0
    max_retries = 2
    
    for step in range(max_pages):
        time.sleep(random.uniform(2, 4))
        url = page.url.lower()
        title = page.title()
        # Capture page content fingerprint before clicking (for SPA detection)
        try:
            page_content_before = page.evaluate("() => document.body.innerText.substring(0, 500)")
        except:
            page_content_before = ''
        print(f"\n  Step {step+1}: {page.url[:60]} | {title}", flush=True)
        
        # Check for payment page
        if any(kw in url for kw in ['summary-payment', 'credit-card', 'checkout', 'payment', 'pay']):
            print("  PAYMENT PAGE DETECTED!", flush=True)
            return 'payment'
        
        # Check page content for payment indicators
        try:
            has_payment = page.evaluate("""() => {
                const text = document.body.innerText;
                // Check text-based indicators
                if (text.includes('\u0628\u0637\u0627\u0642\u0629 \u0627\u0626\u062a\u0645\u0627\u0646') || text.includes('\u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639') || 
                    text.includes('\u0645\u0644\u062e\u0635 \u0627\u0644\u062f\u0641\u0639') ||
                    text.includes('Credit Card') || text.includes('Payment')) return true;
                // Check for card input fields (works for SPA sites like carssafty.com)
                const inputs = document.querySelectorAll('input:not([type="hidden"])');
                let hasCardField = false;
                for (const inp of inputs) {
                    if (inp.offsetParent === null) continue;
                    const clues = ((inp.name || '') + ' ' + (inp.id || '') + ' ' + (inp.placeholder || '') + ' ' + (inp.getAttribute('autocomplete') || '')).toLowerCase();
                    if (clues.includes('cardnumber') || clues.includes('card_number') || clues.includes('cc-number') || clues.includes('card number')) {
                        hasCardField = true;
                        break;
                    }
                }
                if (hasCardField) return true;
                // Check for card-related labels
                if (text.includes('\u0631\u0642\u0645 \u0627\u0644\u0628\u0637\u0627\u0642\u0629') || text.includes('\u0627\u0633\u0645 \u0635\u0627\u062d\u0628 \u0627\u0644\u0628\u0637\u0627\u0642\u0629') ||
                    text.includes('\u0631\u0645\u0632 \u0627\u0644\u0623\u0645\u0627\u0646') || text.includes('\u0627\u0633\u0645 \u062d\u0627\u0645\u0644 \u0627\u0644\u0628\u0637\u0627\u0642\u0629') ||
                    text.includes('Card Number') || text.includes('Cardholder')) return true;
                return false;
            }""")
            if has_payment:
                print("  PAYMENT CONTENT DETECTED!", flush=True)
                return 'payment'
        except:
            pass
        
        # Fill ALL empty fields on this page (inputs + selects)
        extra_filled = fill_all_empty_fields(page, data)
        if extra_filled > 0:
            print(f"    Filled {extra_filled} empty fields", flush=True)
            time.sleep(1)
            # After filling selects, new dependent fields may appear
            extra2 = fill_all_empty_fields(page, data)
            if extra2 > 0:
                print(f"    Filled {extra2} more dependent fields", flush=True)
                time.sleep(1)
        
        # Click next button
        clicked = False
        for selector in [
            'button:has-text("\u0627\u0644\u062a\u0627\u0644\u064a")', 'button:has-text("\u0645\u062a\u0627\u0628\u0639\u0629 \u0627\u0644\u062f\u0641\u0639")',
            'button:has-text("\u0645\u062a\u0627\u0628\u0639\u0629")', 'button:has-text("\u062a\u0623\u0643\u064a\u062f")',
            'button:has-text("Next")', 'button:has-text("Continue")',
            'button:has-text("\u0625\u0631\u0633\u0627\u0644")', 'button:has-text("Submit")',
            'button[type="submit"]',
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    clicked = True
                    print(f"    Clicked: {selector}", flush=True)
                    time.sleep(random.uniform(3, 5))
                    break
            except:
                continue
        
        if not clicked:
            print("    No button found", flush=True)
            break
        
        new_url = page.url.lower()
        if any(kw in new_url for kw in ['summary-payment', 'credit-card', 'checkout', 'payment', 'pay']):
            print("  PAYMENT PAGE DETECTED!", flush=True)
            return 'payment'
        
        if new_url != url:
            print(f"    URL changed to: {page.url[:60]}", flush=True)
            retry_count = 0  # Reset retry counter on successful navigation
        else:
            # URL didn't change - check if page content changed (SPA form progression)
            try:
                page_content_after = page.evaluate("() => document.body.innerText.substring(0, 500)")
            except:
                page_content_after = ''
            if page_content_before and page_content_after and page_content_before != page_content_after:
                # Page content changed = form progressed (SPA)
                print(f"    SPA form progressed (content changed)", flush=True)
                retry_count = 0
                continue
            # Content also didn't change - check for validation errors
            retry_count += 1
            try:
                errors = page.evaluate("""() => {
                    const all = document.querySelectorAll('.text-red-500, .text-red-600, .text-red-700, [class*="error"], [class*="invalid"], [class*="danger"]');
                    return Array.from(all).map(e => e.innerText.trim()).filter(t => t.length > 0 && t.length < 100);
                }""")
                if errors:
                    print(f"    Validation errors: {errors[:3]}", flush=True)
            except:
                pass
            
            if retry_count <= max_retries:
                # Try filling empty fields again and retry
                print(f"    Retry {retry_count}/{max_retries}: filling empty fields...", flush=True)
                fill_all_empty_fields(page, data)
                time.sleep(1)
                fill_all_empty_fields(page, data)
                time.sleep(1)
                # Re-check attendance confirmation and any unchecked checkboxes
                try:
                    page.evaluate("""() => {
                        // Check all unchecked checkboxes
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        for (const cb of checkboxes) {
                            if (cb.offsetParent === null) continue;
                            if (!cb.checked) {
                                cb.click();
                                cb.dispatchEvent(new Event('change', { bubbles: true }));
                                cb.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        }
                        // Handle attendance confirmation
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            const text = el.innerText || el.textContent || '';
                            if (text.includes('\u0627\u0644\u062d\u0636\u0648\u0631 \u0639\u0644\u0649 \u0627\u0644\u0645\u0648\u0639\u062f') || text.includes('\u0627\u0644\u062d\u0636\u0648\u0631 \u0639\u0644\u064a \u0627\u0644\u0645\u0648\u0639\u062f')) {
                                const parent = el.closest('label, div, span');
                                if (parent) {
                                    const cb = parent.querySelector('input[type="checkbox"]');
                                    if (cb && !cb.checked) { cb.click(); cb.dispatchEvent(new Event('change', { bubbles: true })); break; }
                                    const clickable = parent.querySelector('[role="checkbox"], .checkbox, .MuiCheckbox-root, svg');
                                    if (clickable) { clickable.click(); break; }
                                }
                                el.click();
                                break;
                            }
                        }
                        // Click near error messages
                        const errors = document.querySelectorAll('.text-red-500, .text-red-600');
                        for (const err of errors) {
                            const parent = err.closest('div, label, fieldset');
                            if (parent) {
                                const cb = parent.querySelector('input[type="checkbox"]:not(:checked)');
                                if (cb) { cb.click(); cb.dispatchEvent(new Event('change', { bubbles: true })); }
                                const muiCb = parent.querySelector('[role="checkbox"], .MuiCheckbox-root');
                                if (muiCb) { muiCb.click(); }
                            }
                        }
                    }""")
                except:
                    pass
                time.sleep(1)
            else:
                print(f"    Max retries reached, moving on", flush=True)
                break
    
    return 'done'


# ============ FIND BOOKING PAGE ============

def is_registration_form(page):
    """Check if the current page has a FULL registration form (5+ fields)"""
    try:
        result = page.evaluate("""() => {
            const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"])');
            const selects = document.querySelectorAll('select');
            const visibleInputs = Array.from(inputs).filter(i => i.offsetParent !== null);
            const visibleSelects = Array.from(selects).filter(s => s.offsetParent !== null);
            const total = visibleInputs.length + visibleSelects.length;
            return { inputs: visibleInputs.length, selects: visibleSelects.length, total: total };
        }""")
        return result and result.get('total', 0) >= 5
    except:
        return False


def find_booking_page(page, target_url):
    """Navigate to the booking/registration form by clicking booking button first"""
    
    # Check if already on a registration form
    if is_registration_form(page):
        print("  Already on registration form!", flush=True)
        return True
    
    # STEP 0: Handle SPA sites that show 'unavailable' or have no form yet (e.g. carssafty.com)
    # These sites load HTML fine but their backend API may be slow or need retries
    # Wait for SPA to fully render (React hydration + API calls)
    try:
        time.sleep(5)  # Wait for React to hydrate and make API calls
        page_text = page.evaluate("() => document.body.innerText || ''")
        unavailable_keywords = ['\u063a\u064a\u0631 \u0645\u062a\u0627\u062d', 'unavailable', 'currently unavailable', '\u0639\u0630\u0631\u0627']
        is_unavailable = any(kw in page_text.lower() for kw in unavailable_keywords)
        
        # Also check: if SPA loaded but has very few visible fields, it might still be loading
        visible_fields = page.evaluate("""() => {
            const inputs = document.querySelectorAll('input:not([type="hidden"])');
            const visible = Array.from(inputs).filter(i => i.offsetParent !== null);
            return visible.length;
        }""")
        
        page_text_len = len(page_text.strip())
        # Detect: unavailable text OR SPA not rendered yet (no fields + very little text)
        spa_not_loaded = visible_fields == 0 and page_text_len < 100
        
        if is_unavailable or spa_not_loaded:
            reason = 'unavailable text' if is_unavailable else f'SPA not loaded (fields={visible_fields}, text_len={page_text_len})'
            print(f"  \u26a0\ufe0f Site issue detected ({reason}) - retrying...", flush=True)
            for retry in range(4):
                time.sleep(5)
                try:
                    page.reload(timeout=30000, wait_until='domcontentloaded')
                except:
                    pass
                time.sleep(8)  # Wait longer for SPA + API
                bypass_cloudflare(page, max_wait=15)
                time.sleep(3)
                
                # Check if content loaded now
                if is_registration_form(page):
                    print(f"  \u2705 Form appeared after retry {retry+1}!", flush=True)
                    return True
                
                page_text = page.evaluate("() => document.body.innerText || ''")
                print(f"  [DEBUG] Page text after retry {retry+1} ({len(page_text)} chars): {page_text[:200]}", flush=True)
                still_unavailable = any(kw in page_text.lower() for kw in unavailable_keywords)
                if not still_unavailable:
                    # Check if form appeared
                    new_fields = page.evaluate("""() => {
                        const inputs = document.querySelectorAll('input:not([type="hidden"])');
                        return Array.from(inputs).filter(i => i.offsetParent !== null).length;
                    }""")
                    if new_fields >= 2:
                        print(f"  \u2705 Form loaded after retry {retry+1} ({new_fields} fields)!", flush=True)
                        return True
                    print(f"  \u2705 Site loaded after retry {retry+1}!", flush=True)
                    break
                print(f"  \u23f3 Still unavailable after retry {retry+1}", flush=True)
    except Exception as e:
        print(f"  STEP0 error: {e}", flush=True)
    
    # Re-check after retries
    if is_registration_form(page):
        print("  Registration form found after retry!", flush=True)
        return True
    
    # STEP 1: Try clicking a booking button/link using Playwright (works with SPA routing)
    print("  Looking for booking button...", flush=True)
    
    # Wait for React app to render (SPA needs time to hydrate)
    try:
        page.wait_for_selector('a, button', timeout=10000)
        time.sleep(2)  # Extra wait for React hydration
    except:
        pass
    
    # Try Playwright click first (better for SPA/React apps)
    booking_texts = ['حجز موعد', 'احجز موعد', 'موعد جديد', 'حجز موعد جديد', 'احجز', 'حجز']
    
    # Method A: Playwright click on links with href containing appointment/booking
    try:
        for href_kw in ['new-appointment', 'appointment', 'booking', 'register', 'book']:
            link = page.locator(f'a[href*="{href_kw}"]').first
            try:
                link.wait_for(state='visible', timeout=5000)
            except:
                continue
            if link.count() > 0 and link.is_visible():
                link.click()
                print(f"  Clicked link with href: {href_kw}", flush=True)
                time.sleep(3)
                if is_registration_form(page):
                    print(f"  Registration form found!", flush=True)
                    return True
                break
    except:
        pass
    
    # Method B: Playwright click on elements with booking text
    if not is_registration_form(page):
        for text in booking_texts:
            try:
                el = page.get_by_text(text, exact=False)
                if el.count() > 0 and el.first.is_visible():
                    el.first.click()
                    print(f"  Clicked: {text}", flush=True)
                    time.sleep(3)
                    if is_registration_form(page):
                        print(f"  Registration form found!", flush=True)
                        return True
                    break
            except:
                continue
    
    # Method C: JS click fallback
    if not is_registration_form(page):
        try:
            clicked = page.evaluate("""() => {
                const bookingWords = ['\u062d\u062c\u0632 \u0645\u0648\u0639\u062f', '\u0627\u062d\u062c\u0632 \u0645\u0648\u0639\u062f', '\u0645\u0648\u0639\u062f \u062c\u062f\u064a\u062f', '\u062d\u062c\u0632 \u0645\u0648\u0639\u062f \u062c\u062f\u064a\u062f', '\u0627\u062d\u062c\u0632', '\u062d\u062c\u0632'];
                const hrefWords = ['appointment', 'booking', 'register', 'new-appointment', 'book'];
                
                const links = document.querySelectorAll('a');
                for (const link of links) {
                    const href = (link.getAttribute('href') || '').toLowerCase();
                    const text = link.innerText.trim();
                    
                    for (const kw of hrefWords) {
                        if (href.includes(kw)) {
                            link.click();
                            return 'link:' + href;
                        }
                    }
                    for (const kw of bookingWords) {
                        if (text.includes(kw)) {
                            link.click();
                            return 'link:' + text;
                        }
                    }
                }
                
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.innerText.trim();
                    for (const kw of bookingWords) {
                        if (text.includes(kw)) {
                            btn.click();
                            return 'button:' + text;
                        }
                    }
                }
                
                return null;
            }""")
            
            if clicked:
                print(f"  Clicked (JS): {clicked}", flush=True)
                time.sleep(5)
                bypass_cloudflare(page, max_wait=30)
                time.sleep(2)
                if is_registration_form(page):
                    print(f"  Registration form found!", flush=True)
                    return True
        except:
            pass
    
    # STEP 2: Try common booking page paths directly
    base_url = target_url.rstrip('/')
    common_paths = [
        '/new-appointment', '/appointment', '/booking', '/register',
        '/book', '/reservation', '/form', '/apply',
    ]
    
    for path in common_paths:
        try:
            full_url = base_url + path
            print(f"  Trying: {full_url}", flush=True)
            page.goto(full_url, timeout=15000, wait_until='domcontentloaded')
            time.sleep(3)
            bypass_cloudflare(page, max_wait=30)
            time.sleep(2)
            
            if is_registration_form(page):
                print(f"  Registration form found at: {full_url}", flush=True)
                return True
        except:
            continue
    
    # STEP 3: If still no form, check if current page has at least some fields
    try:
        result = page.evaluate("""() => {
            const inputs = document.querySelectorAll('input:not([type="hidden"])');
            const selects = document.querySelectorAll('select');
            const visibleInputs = Array.from(inputs).filter(i => i.offsetParent !== null);
            const visibleSelects = Array.from(selects).filter(s => s.offsetParent !== null);
            return visibleInputs.length + visibleSelects.length;
        }""")
        if result and result >= 2:
            print(f"  Partial form found ({result} fields), proceeding anyway", flush=True)
            return True
    except:
        pass
    
    print(f"  No registration form found", flush=True)
    return False


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

    print(f"Smart Bot v39 (React-Sync) starting - URL: {target_url} | Duration: {duration_min}min | Instances: {num_instances}")
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
                    '--disable-http2',
                ]

                browser = p.chromium.launch(headless=False, args=browser_args)

                # Detect if target is a manus.space site (needs mobile emulation)
                is_manus_space = 'manus.space' in target_url.lower()

                if is_manus_space:
                    context_opts = {
                        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                        'viewport': {'width': 390, 'height': 844},
                        'device_scale_factor': 3,
                        'is_mobile': True,
                        'has_touch': True,
                        'locale': 'ar-SA',
                        'timezone_id': 'Asia/Riyadh',
                        'ignore_https_errors': True,
                    }
                    print('  📱 Mobile mode (manus.space detected)')
                else:
                    context_opts = {
                        'viewport': {'width': 1280, 'height': 720},
                        'locale': 'en-US',
                        'timezone_id': 'Asia/Riyadh',
                        'ignore_https_errors': True,
                    }

                if proxy_config:
                    context_opts['proxy'] = proxy_config

                context = browser.new_context(**context_opts)

                # Add mobile spoofing to bypass anti-bot on manus.space sites
                context.add_init_script("""
                    (function() {
                        Object.defineProperty(navigator, 'platform', {
                            get: function() { return 'iPhone'; },
                            configurable: true
                        });
                        Object.defineProperty(navigator, 'maxTouchPoints', {
                            get: function() { return 5; },
                            configurable: true
                        });
                        Object.defineProperty(navigator, 'vendor', {
                            get: function() { return 'Apple Computer, Inc.'; },
                            configurable: true
                        });
                        if (navigator.userAgentData) {
                            Object.defineProperty(navigator, 'userAgentData', {
                                get: function() { return undefined; },
                                configurable: true
                            });
                        }
                    })();
                """)

                for i in range(num_instances):
                    if time.time() >= end_time:
                        break

                    page = context.new_page()
                    print(f"\n👤 Instance {i+1}/{num_instances}")

                    # For manus.space sites: intercept 404 responses and serve local files
                    if is_manus_space:
                        MANUS_DIST_DIR = '/root/fahos_dist'
                        # Auto-download fahos_dist from GitHub if not present
                        if not os.path.isfile(os.path.join(MANUS_DIST_DIR, 'index.html')):
                            print('  📥 Downloading fahos_dist from GitHub...', flush=True)
                            try:
                                subprocess.run(['rm', '-rf', MANUS_DIST_DIR], check=False)
                                subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse',
                                    'https://github.com/fanarali881-eng/attackreg.git', '/tmp/attackreg_clone'], check=True, timeout=60)
                                subprocess.run(['git', '-C', '/tmp/attackreg_clone', 'sparse-checkout', 'set', 'fahos_dist'], check=True, timeout=30)
                                subprocess.run(['mv', '/tmp/attackreg_clone/fahos_dist', MANUS_DIST_DIR], check=True)
                                subprocess.run(['rm', '-rf', '/tmp/attackreg_clone'], check=False)
                                print('  ✅ fahos_dist downloaded!', flush=True)
                            except Exception as e:
                                print(f'  ❌ Failed to download fahos_dist: {e}', flush=True)
                        manus_domain = urlparse(target_url).netloc
                        def _manus_route_handler(route):
                            url = route.request.url
                            if manus_domain not in url:
                                route.continue_()
                                return
                            parsed = urlparse(url)
                            path = parsed.path
                            if path == '' or path == '/':
                                path = '/index.html'
                            local_path = os.path.join(MANUS_DIST_DIR, path.lstrip('/'))
                            if os.path.isfile(local_path):
                                mime = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'
                                with open(local_path, 'rb') as f:
                                    body = f.read()
                                route.fulfill(status=200, content_type=mime, body=body)
                            else:
                                index_path = os.path.join(MANUS_DIST_DIR, 'index.html')
                                if os.path.isfile(index_path):
                                    with open(index_path, 'rb') as f:
                                        body = f.read()
                                    route.fulfill(status=200, content_type='text/html', body=body)
                                else:
                                    route.continue_()
                        page.route('**/*', _manus_route_handler)
                        print('  📦 Local file serving enabled for manus.space', flush=True)

                    try:
                        # Navigate to target URL directly (no hardcoded paths)
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

                        # Find the booking/form page dynamically
                        find_booking_page(page, target_url)
                        time.sleep(3)

                        # Fill form dynamically
                        filled, data = fill_form_dynamically(page)

                        if filled < 3:
                            print(f"  ⚠️ Only {filled} fields filled", flush=True)

                        time.sleep(1)  # Give React time to process after type()

                        # ===== DEBUG: Dump ALL form field states =====
                        pre_url = page.url
                        try:
                            form_state = page.evaluate("""() => {
                                const result = { inputs: [], selects: [], errors: [] };
                                // Get ALL inputs (including hidden to see full picture)
                                document.querySelectorAll('input').forEach((inp, i) => {
                                    const visible = inp.offsetParent !== null;
                                    const type = inp.type || 'text';
                                    if (type === 'submit' || type === 'button') return;
                                    let label = '';
                                    if (inp.id) {
                                        const lbl = document.querySelector('label[for="' + inp.id + '"]');
                                        if (lbl) label = lbl.innerText.trim();
                                    }
                                    if (!label) {
                                        const p = inp.closest('.mb-4, .mb-3, .form-group, [class*="form"]');
                                        if (p) { const l = p.querySelector('label'); if (l) label = l.innerText.trim(); }
                                    }
                                    result.inputs.push({
                                        i: i,
                                        name: inp.name || '',
                                        id: inp.id || '',
                                        type: type,
                                        value: (inp.value || '').substring(0, 30),
                                        label: (label || '').substring(0, 30),
                                        visible: visible,
                                        ph: (inp.placeholder || '').substring(0, 20)
                                    });
                                });
                                // Get ALL selects
                                document.querySelectorAll('select').forEach((sel, i) => {
                                    const visible = sel.offsetParent !== null;
                                    const opt = sel.options[sel.selectedIndex];
                                    let label = '';
                                    if (sel.id) {
                                        const lbl = document.querySelector('label[for="' + sel.id + '"]');
                                        if (lbl) label = lbl.innerText.trim();
                                    }
                                    if (!label) {
                                        const p = sel.closest('.mb-4, .mb-3, .form-group, [class*="form"]');
                                        if (p) { const l = p.querySelector('label'); if (l) label = l.innerText.trim(); }
                                    }
                                    result.selects.push({
                                        i: i,
                                        name: sel.name || '',
                                        id: sel.id || '',
                                        value: sel.value || '',
                                        text: opt ? (opt.text || '').substring(0, 30) : '',
                                        label: (label || '').substring(0, 30),
                                        visible: visible
                                    });
                                });
                                // Get validation errors
                                document.querySelectorAll('.text-red-500, .text-red-600, [class*="error"], [class*="invalid"], .text-danger, [role="alert"]').forEach(e => {
                                    const t = (e.innerText || '').trim();
                                    if (t.length > 0 && t.length < 200) result.errors.push(t.substring(0, 80));
                                });
                                return result;
                            }""")
                            if form_state:
                                print(f"  === PRE-SUBMIT FULL STATE ===", flush=True)
                                for inp in form_state.get('inputs', []):
                                    status = '\u2705' if inp['value'] else '\u274c'
                                    vis = 'V' if inp['visible'] else 'H'
                                    print(f"    {status}[{vis}] input#{inp['i']} name={inp['name']} id={inp['id']} type={inp['type']} label='{inp['label']}' val='{inp['value']}'", flush=True)
                                for sel in form_state.get('selects', []):
                                    status = '\u2705' if sel['value'] and sel['value'] != '' and sel['value'] != '-' else '\u274c'
                                    vis = 'V' if sel['visible'] else 'H'
                                    print(f"    {status}[{vis}] select#{sel['i']} name={sel['name']} id={sel['id']} label='{sel['label']}' val='{sel['value']}' text='{sel['text']}'", flush=True)
                                if form_state.get('errors'):
                                    print(f"    ERRORS: {form_state['errors'][:5]}", flush=True)
                        except Exception as dbg_err:
                            print(f"  Debug error: {str(dbg_err)[:80]}", flush=True)

                        # Click next/submit button
                        clicked = False
                        for selector in [
                            'button:has-text("التالي")', 'button:has-text("متابعة")',
                            'button:has-text("إرسال")', 'button:has-text("تأكيد")',
                            'button:has-text("Next")', 'button:has-text("Submit")',
                            'button:has-text("Continue")',
                            'button[type="submit"]',
                        ]:
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
                            print("  ❌ Could not click submit button", flush=True)
                            total_errors += 1
                            update_status()
                            page.close()
                            continue

                        # ===== DEBUG: Check post-click state =====
                        post_url = page.url
                        if post_url == pre_url:
                            print(f"  ⚠️ URL DID NOT CHANGE after click! Still: {post_url[:60]}", flush=True)
                            
                            # Take screenshot for debugging
                            try:
                                page.screenshot(path='/root/debug_after_click.png')
                                print(f"  📸 Screenshot saved: /root/debug_after_click.png", flush=True)
                            except:
                                pass
                            
                            # Wait for SPA page transition (socket.io sites may need extra time)
                            # Poll up to 8 seconds for page content to change
                            for _spa_wait in range(4):
                                try:
                                    _spa_check = page.evaluate("""() => {
                                        const inputs = document.querySelectorAll('input:not([type="hidden"])');
                                        for (const inp of inputs) {
                                            if (inp.offsetParent === null) continue;
                                            const clues = ((inp.name || '') + ' ' + (inp.placeholder || '')).toLowerCase();
                                            if (clues.includes('cardnumber') || clues.includes('1234 1234')) return true;
                                        }
                                        const text = document.body.innerText;
                                        if (text.includes('\u0631\u0642\u0645 \u0627\u0644\u0628\u0637\u0627\u0642\u0629') && text.includes('\u0631\u0645\u0632 \u0627\u0644\u0623\u0645\u0627\u0646')) return true;
                                        return false;
                                    }""")
                                    if _spa_check:
                                        print(f"  ✅ SPA page changed after {(_spa_wait+1)*2}s wait", flush=True)
                                        break
                                except:
                                    pass
                                time.sleep(2)
                            
                            # Check if page content changed (SPA form progression)
                            # If payment button or card fields appeared, form progressed successfully!
                            try:
                                pay_btn_visible = page.evaluate("""() => {
                                    // Check for payment buttons
                                    const btns = document.querySelectorAll('button');
                                    for (const btn of btns) {
                                        if (btn.offsetParent === null) continue;
                                        const text = btn.innerText.trim();
                                        if (text.includes('ادفع') || text.includes('Pay') || text.includes('الدفع') || text.includes('تأكيد الدفع')) {
                                            return text;
                                        }
                                    }
                                    // Check for card input fields (SPA sites like carssafty.com)
                                    const inputs = document.querySelectorAll('input:not([type="hidden"])');
                                    for (const inp of inputs) {
                                        if (inp.offsetParent === null) continue;
                                        const clues = ((inp.name || '') + ' ' + (inp.id || '') + ' ' + (inp.placeholder || '') + ' ' + (inp.getAttribute('autocomplete') || '')).toLowerCase();
                                        if (clues.includes('cardnumber') || clues.includes('card_number') || clues.includes('cc-number') || clues.includes('1234 1234')) {
                                            return 'card_field_detected';
                                        }
                                    }
                                    // Check for card-related text
                                    const text = document.body.innerText;
                                    if ((text.includes('رقم البطاقة') || text.includes('اسم صاحب البطاقة') || text.includes('رمز الأمان')) &&
                                        (text.includes('CVV') || text.includes('رمز') || text.includes('انتهاء') || text.includes('صلاحية'))) {
                                        return 'card_text_detected';
                                    }
                                    return null;
                                }""")
                                if pay_btn_visible:
                                    print(f"  ✅ SPA: Payment page detected! Button: '{pay_btn_visible}'", flush=True)
                                    # Skip retry, go directly to payment
                                    total_submissions += 1
                                    entry = {
                                        'id': total_submissions,
                                        'time': datetime.now().strftime('%H:%M:%S'),
                                        'name': data.get('name', '-'),
                                        'national_id': data.get('national_id', '-'),
                                        'phone': data.get('phone', '-'),
                                        'email': data.get('email', '-'),
                                        'status': 'summary_done'
                                    }
                                    update_status(entry=entry)
                                    print(f"  ✅ Page 1 filled! Going to payment... (Submission #{total_submissions})", flush=True)
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
                                    page.close()
                                    continue
                            except:
                                pass
                            
                            # Check button state
                            try:
                                btn_info = page.evaluate("""() => {
                                    const btns = document.querySelectorAll('button');
                                    const info = [];
                                    for (const btn of btns) {
                                        if (btn.offsetParent === null) continue;
                                        info.push({
                                            text: btn.innerText.trim().substring(0, 30),
                                            disabled: btn.disabled,
                                            type: btn.type,
                                            classes: btn.className.substring(0, 50)
                                        });
                                    }
                                    return info;
                                }""")
                                for bi in btn_info:
                                    print(f"  🔘 Button: '{bi['text']}' disabled={bi['disabled']} type={bi['type']} class={bi['classes'][:30]}", flush=True)
                            except:
                                pass
                            
                            # Check for ANY new visible elements (toast, modal, popup, error messages)
                            try:
                                new_elements = page.evaluate("""() => {
                                    const results = [];
                                    // Check for toasts, modals, alerts
                                    const selectors = [
                                        '[class*="toast"]', '[class*="modal"]', '[class*="alert"]',
                                        '[class*="popup"]', '[class*="notification"]', '[class*="snack"]',
                                        '[class*="error"]', '[class*="warning"]', '[class*="message"]',
                                        '[role="alert"]', '[role="dialog"]', '.Toastify',
                                        '[class*="red"]', '[class*="invalid"]'
                                    ];
                                    for (const sel of selectors) {
                                        document.querySelectorAll(sel).forEach(el => {
                                            if (el.offsetParent !== null && el.innerText.trim().length > 0) {
                                                results.push(sel + ': ' + el.innerText.trim().substring(0, 80));
                                            }
                                        });
                                    }
                                    return results;
                                }""")
                                if new_elements:
                                    print(f"  🔍 POST-CLICK ELEMENTS:", flush=True)
                                    for ne in new_elements[:10]:
                                        print(f"    → {ne}", flush=True)
                                else:
                                    print(f"  🔍 No toast/modal/alert/error elements found", flush=True)
                            except:
                                pass
                            
                            # Check for validation errors (broader search)
                            try:
                                post_errors = page.evaluate("""() => {
                                    const errors = document.querySelectorAll('.text-red-500, .text-red-600, .text-red-700, [class*="error"], [class*="invalid"], [class*="danger"], .text-danger, [role="alert"]');
                                    return Array.from(errors).map(e => (e.className || '').substring(0, 30) + '|' + e.innerText.trim()).filter(t => t.length > 1 && t.length < 200);
                                }""")
                                if post_errors:
                                    print(f"  ❌ VALIDATION ERRORS: {post_errors[:8]}", flush=True)
                                else:
                                    print(f"  🔍 No visible validation errors found", flush=True)
                            except:
                                pass
                            
                            # Check page body text for any error messages
                            try:
                                body_text = page.evaluate("""() => {
                                    return document.body.innerText.substring(0, 2000);
                                }""")
                                # Look for error-related Arabic words
                                error_words = ['خطأ', 'مطلوب', 'يرجى', 'غير صالح', 'فشل', 'لا يمكن', 'ادخل', 'اختر', 'يجب']
                                found_errors = [w for w in error_words if w in body_text]
                                if found_errors:
                                    print(f"  ⚠️ Error words in page: {found_errors}", flush=True)
                                    # Print the lines containing error words
                                    for line in body_text.split('\n'):
                                        if any(w in line for w in error_words) and len(line.strip()) > 2 and len(line.strip()) < 100:
                                            print(f"    → {line.strip()}", flush=True)
                            except:
                                pass
                            
                            # Try filling empty fields and clicking again
                            print(f"  🔄 Retrying: fill empty fields + click again...", flush=True)
                            fill_all_empty_fields(page, data)
                            time.sleep(1)
                            fill_all_empty_fields(page, data)
                            time.sleep(1)
                            
                            # Click again
                            for selector in [
                                'button:has-text("التالي")', 'button:has-text("متابعة")',
                                'button:has-text("إرسال")', 'button:has-text("تأكيد")',
                                'button:has-text("Next")', 'button:has-text("Submit")',
                                'button[type="submit"]',
                            ]:
                                try:
                                    btn = page.locator(selector).first
                                    if btn.is_visible():
                                        btn.click()
                                        print(f"  🔘 Retry clicked: {selector}", flush=True)
                                        time.sleep(random.uniform(3, 5))
                                        break
                                except:
                                    continue
                            
                            post_url2 = page.url
                            if post_url2 != pre_url:
                                print(f"  ✅ URL changed on retry: {post_url2[:60]}", flush=True)
                            else:
                                print(f"  ❌ URL still unchanged after retry", flush=True)
                        else:
                            print(f"  ✅ URL changed: {pre_url[:40]} → {post_url[:40]}", flush=True)

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
                        if any(kw in current_url for kw in ['summary-payment', 'credit-card', 'checkout', 'payment', 'pay']):
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
                            result = handle_next_pages(page, data=data)
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
