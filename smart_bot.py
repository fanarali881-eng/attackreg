"""
Smart Universal Form Bot v29 - Fully Dynamic Field Detection
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
        'ar': ['تاريخ الميلاد', 'الميلاد'],
        'en': ['birth', 'dob', 'date_of_birth'],
        'exclude': [],
    },
    'inspection_date': {
        'ar': ['تاريخ الفحص', 'تاريخ', 'التاريخ', 'موعد الفحص'],
        'en': ['date', 'inspection_date', 'appointment_date', 'schedule'],
        'exclude': ['ميلاد', 'birth', 'انتهاء', 'expir'],
    },
    'delegate_name': {
        'ar': ['المفوض', 'مفوض', 'أسم المفوض', 'اسم المفوض', 'الوكيل', 'وكيل', 'المندوب', 'مندوب'],
        'en': ['delegate', 'representative', 'agent_name', 'authorized'],
        'exclude': [],
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
}


# ============ DYNAMIC FIELD DETECTION ============

def classify_input_field(clues):
    """Classify an input field based on all available clues (placeholder, label, name, id, aria-label)"""
    clues_lower = clues.lower()
    
    for field_type, keywords in FIELD_KEYWORDS.items():
        # Check exclusions first
        for exc in keywords.get('exclude', []):
            if exc in clues_lower:
                continue
        
        # Check Arabic keywords
        for kw in keywords['ar']:
            if kw in clues:
                return field_type
        
        # Check English keywords
        for kw in keywords['en']:
            if kw in clues_lower:
                return field_type
    
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
                        if any(w in all_clues for w in ['\u062a\u0627\u0631\u064a\u062e', 'date', '\u0645\u0648\u0639\u062f']):
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
                        el.click()
                        time.sleep(random.uniform(0.2, 0.4))
                        el.fill(value)
                        time.sleep(random.uniform(0.1, 0.3))
                        filled += 1
                        print(f"    [refill] {field_type}: {value[:25]}", flush=True)
                except Exception as e:
                    print(f"    [refill] Error {field_type}: {str(e)[:50]}", flush=True)
    except Exception as e:
        print(f"    [refill] Input scan error: {str(e)[:80]}", flush=True)
    
    # STEP B: Fill empty selects using JS dispatchEvent (same as before - this works)
    try:
        sel_filled = page.evaluate("""() => {
            let filled = 0;
            const selects = document.querySelectorAll('select');
            for (const sel of selects) {
                if (sel.offsetParent === null) continue;
                if (sel.value && sel.value !== '' && sel.value !== '-') {
                    const currentOpt = sel.options[sel.selectedIndex];
                    if (currentOpt && !currentOpt.text.includes('\u0627\u062e\u062a\u0631') && !currentOpt.text.includes('Select')) continue;
                }
                const opts = Array.from(sel.options).filter(o => 
                    o.value && o.value !== '' && o.value !== '-' && !o.text.includes('\u0627\u062e\u062a\u0631') && !o.text.includes('Select'));
                if (opts.length > 0) {
                    const choice = opts[Math.floor(Math.random() * opts.length)];
                    sel.value = choice.value;
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                    filled++;
                }
            }
            return filled;
        }""")
        filled += (sel_filled or 0)
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
                        if any(w in all_clues for w in ['\u062a\u0627\u0631\u064a\u062e', 'date', '\u0645\u0648\u0639\u062f']):
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
                
                # Skip if already has a value
                if field.get('value') and len(field['value']) > 2:
                    print(f"    ⏭️ {field_type}: already has value '{field['value'][:20]}'", flush=True)
                    continue
                
                # Fill the field
                try:
                    selector = field.get('selector')
                    if selector:
                        el = page.locator(selector).first
                    else:
                        # Fallback: use nth input
                        el = page.locator(f'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"]):visible').nth(field['index'])
                    
                    if el.is_visible():
                        el.click()
                        time.sleep(random.uniform(0.2, 0.4))
                        el.fill(value)
                        time.sleep(random.uniform(0.1, 0.3))
                        filled += 1
                        print(f"    ✅ {field_type}: {value[:30]}", flush=True)
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
                            page.evaluate(f"""(args) => {{
                                const sel = document.querySelectorAll('select')[{sel['index']}];
                                if (sel) {{
                                    sel.value = args.value;
                                    sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                }}
                            }}""", {'value': choice['value']})
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
                        placeholder_words = ['\u0627\u062e\u062a\u0631', '\u0627\u0644\u0645\u0646\u0637\u0642\u0629', '\u0646\u0648\u0639 \u0627\u0644\u0645\u0631\u0643\u0628\u0629', '\u0627\u0644\u062c\u0646\u0633\u064a\u0629', '\u0628\u0644\u062f', '\u0627\u062e\u062a\u064a\u0627\u0631', 'Select', 'Choose']
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
                    idx = sel['index']
                    page.evaluate(f"""(args) => {{
                        const allSelects = document.querySelectorAll('select');
                        let visibleIdx = 0;
                        for (const s of allSelects) {{
                            if (s.offsetParent === null) continue;
                            if (visibleIdx === args.idx) {{
                                s.value = args.value;
                                s.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                return true;
                            }}
                            visibleIdx++;
                        }}
                        return false;
                    }}""", {'idx': idx, 'value': chosen['value']})
                    filled += 1
                    print(f"    ✅ {field_type}: {chosen['text'][:30]}", flush=True)
                    
                    # Wait for dependent dropdowns to load (region -> center)
                    if field_type in ('region', 'country', 'nationality'):
                        time.sleep(random.uniform(1, 2))
                    else:
                        time.sleep(random.uniform(0.3, 0.6))
                    
                except Exception as e:
                    print(f"    ❌ {field_type}: {str(e)[:60]}", flush=True)
    
    except Exception as e:
        print(f"  ❌ Select detection error: {str(e)[:100]}", flush=True)
    
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
                    
                    elif any(kw in clues for kw in ['holder', 'cardholder', 'name on', 'cc-name', 'حامل', 'الاسم كما', 'card_holder', 'cardname']):
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
                    
                    if (text.includes('رقم البطاقة') || text.includes('Card Number')) { value = data.card_number; fieldName = 'card'; }
                    else if (text.includes('اسم حامل') || text.includes('حامل البطاقة') || text.includes('Cardholder')) { value = data.card_holder; fieldName = 'holder'; }
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
        print(f"\n  Step {step+1}: {page.url[:60]} | {title}", flush=True)
        
        # Check for payment page
        if any(kw in url for kw in ['summary-payment', 'credit-card', 'checkout', 'payment', 'pay']):
            print("  PAYMENT PAGE DETECTED!", flush=True)
            return 'payment'
        
        # Check page content for payment indicators
        try:
            has_payment = page.evaluate("""() => {
                const text = document.body.innerText;
                return text.includes('\u0628\u0637\u0627\u0642\u0629 \u0627\u0626\u062a\u0645\u0627\u0646') || text.includes('\u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639') || 
                       text.includes('\u0645\u0644\u062e\u0635 \u0627\u0644\u062f\u0641\u0639') || text.includes('\u0627\u0644\u0645\u0628\u0644\u063a') ||
                       text.includes('Credit Card') || text.includes('Payment');
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
            # URL didn't change - check for validation errors
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
    
    # STEP 1: Try clicking a booking button/link on the current page
    print("  Looking for booking button...", flush=True)
    
    # Use JavaScript to find and click the first booking-related link/button
    try:
        clicked = page.evaluate("""() => {
            const bookingWords = ['\u062d\u062c\u0632 \u0645\u0648\u0639\u062f', '\u0627\u062d\u062c\u0632 \u0645\u0648\u0639\u062f', '\u0645\u0648\u0639\u062f \u062c\u062f\u064a\u062f', '\u062d\u062c\u0632 \u0645\u0648\u0639\u062f \u062c\u062f\u064a\u062f', '\u0627\u062d\u062c\u0632', '\u062d\u062c\u0632'];
            const hrefWords = ['appointment', 'booking', 'register', 'new-appointment', 'book'];
            
            // Try links first (most common for navigation)
            const links = document.querySelectorAll('a');
            for (const link of links) {
                const href = (link.getAttribute('href') || '').toLowerCase();
                const text = link.innerText.trim();
                
                // Check href keywords
                for (const kw of hrefWords) {
                    if (href.includes(kw)) {
                        link.click();
                        return 'link:' + href;
                    }
                }
                // Check text keywords
                for (const kw of bookingWords) {
                    if (text.includes(kw)) {
                        link.click();
                        return 'link:' + text;
                    }
                }
            }
            
            // Try buttons
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
            print(f"  Clicked: {clicked}", flush=True)
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

    print(f"Smart Bot v31 (Dynamic) starting - URL: {target_url} | Duration: {duration_min}min | Instances: {num_instances}")
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
