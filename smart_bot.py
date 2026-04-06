"""
Smart Universal Form Bot v62 - Fill ALL commissioner fields via JS evaluate (no uncheck delegate)
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
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
import urllib.request
import ssl

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
    'Al Rajhi': ['554575', '968205', '458838', '458837', '468564', '468565', '409201', '429927', '445827', '457553', '484783'],
    'Saudi National Bank (SNB)': ['554180', '556676', '556675', '588850', '968202', '417633', '417634',
        '223379', '223398', '412113', '430258', '430259', '430260', '445303', '450766', '465154',
        '482052', '483178', '485005', '485042', '512220', '512464', '515079', '515530', '516138',
        '518694', '519310', '519341', '523954', '524197', '524388', '525688', '528597', '529415',
        '531505', '532446', '533964', '534797', '535311', '535825', '536369', '539034', '540613',
        '545205', '548255', '549699', '552075', '552077', '555610'],
    'Riyad Bank': ['559322', '558563', '968209', '454313', '454314', '489318', '454683', '457927'],
    'SABB': ['422818', '422819', '605141', '968204', '431361', '456893'],
    'Saudi Fransi': ['440795', '552360', '588845', '968208', '440647', '457865'],
    'Arab National Bank': ['455036', '455037', '549400', '588848', '968203'],
    'Alinma Bank': ['552363', '968206', '426897', '485457', '432328'],
    'Bank Al-Jazira': ['445564', '968211', '409201'],
    'Saudi Investment Bank': ['552384', '589206', '968207', '483010'],
    'Samba': ['552250', '552089', '446392', '446672'],
    'Al Bilad Bank': ['636120', '968201', '468540'],
    'Saudi Awwal Bank (SAB)': ['552438', '552375', '558854', '558848', '557606', '548979', '512060'],
    'D360 Bank': ['428068', '431266', '433521', '435733', '442463', '459931'],
    'Gulf International Bank (GIB)': ['400399', '404116', '414026', '417487', '422862'],
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

# Persistent name tracking - names saved to file so they NEVER repeat even across restarts
_USED_NAMES_FILE = '/root/used_names.txt'
_used_names = set()

def _load_used_names():
    """Load previously used names from file on disk."""
    global _used_names
    try:
        if os.path.exists(_USED_NAMES_FILE):
            with open(_USED_NAMES_FILE, 'r', encoding='utf-8') as f:
                _used_names = set(line.strip() for line in f if line.strip())
            print(f"  \U0001f4c2 Loaded {len(_used_names)} previously used names", flush=True)
    except Exception as e:
        print(f"  \u26a0\ufe0f Could not load used names: {e}", flush=True)

def _save_name(name):
    """Append a new name to the persistent file."""
    try:
        with open(_USED_NAMES_FILE, 'a', encoding='utf-8') as f:
            f.write(name + '\n')
    except:
        pass

# Load names from previous runs on startup
_load_used_names()

def gen_name():
    """Generate a unique 4-part Saudi name (first + father + grandfather + family).
    Names never repeat - not in this session and not in any previous session."""
    for _ in range(1000):
        first = random.choice(SAUDI_MALE_FIRST if random.random() > 0.3 else SAUDI_FEMALE_FIRST)
        father = random.choice(SAUDI_MALE_FIRST)
        grandfather = random.choice(SAUDI_MALE_FIRST)
        last = random.choice(SAUDI_LAST)
        full_name = f"{first} {father} {grandfather} {last}"
        if full_name not in _used_names:
            _used_names.add(full_name)
            _save_name(full_name)
            return full_name
    # Fallback: if somehow all 4M+ combinations exhausted, add random digits
    first = random.choice(SAUDI_MALE_FIRST if random.random() > 0.3 else SAUDI_FEMALE_FIRST)
    father = random.choice(SAUDI_MALE_FIRST)
    grandfather = random.choice(SAUDI_MALE_FIRST)
    last = random.choice(SAUDI_LAST)
    return f"{first} {father} {grandfather} {last}"

def gen_email():
    user = ''.join(random.choices(string.ascii_lowercase, k=random.randint(6, 10)))
    user += str(random.randint(1, 999))
    return f"{user}@{random.choice(['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com'])}"

def gen_plate_number():
    return str(random.randint(1, 9999))

# Persistent card number tracking - never repeat even across restarts
_USED_CARDS_FILE = '/root/used_cards.txt'
_used_cards = set()

def _load_used_cards():
    """Load previously used card numbers from file on disk."""
    global _used_cards
    try:
        if os.path.exists(_USED_CARDS_FILE):
            with open(_USED_CARDS_FILE, 'r', encoding='utf-8') as f:
                _used_cards = set(line.strip() for line in f if line.strip())
            print(f"  \U0001f4b3 Loaded {len(_used_cards)} previously used card numbers", flush=True)
    except Exception as e:
        print(f"  \u26a0\ufe0f Could not load used cards: {e}", flush=True)

def _save_card(card_num):
    """Append a new card number to the persistent file."""
    try:
        with open(_USED_CARDS_FILE, 'a', encoding='utf-8') as f:
            f.write(card_num + '\n')
    except:
        pass

# Load cards from previous runs on startup
_load_used_cards()

def gen_card_number():
    """Generate a unique card number with valid Luhn checksum.
    Card numbers never repeat - not in this session and not in any previous session."""
    for _ in range(1000):
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
        card_num = ''.join(str(d) for d in digits)
        if card_num not in _used_cards:
            _used_cards.add(card_num)
            _save_card(card_num)
            return card_num, bank_name
    # Fallback (practically impossible)
    return card_num, bank_name

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

# ============ CAPSOLVER CAPTCHA SOLVING ============
CAPSOLVER_API_KEY = os.environ.get('CAPSOLVER_KEY', 'CAP-96A43200A31AF2F850CBE659AFC4280C154409585ABA50AC7B1EA7F67A6E7B10')

def solve_captcha_image(page):
    """Find captcha image on page, send to CapSolver, return solved text"""
    try:
        # Try to get captcha image as base64
        captcha_b64 = page.evaluate("""() => {
            // Strategy 1: Find img near captcha input
            const captchaInput = document.querySelector('input[name="captcha"], input[id="captcha"], input[name*="captcha"], input[id*="captcha"]');
            if (captchaInput) {
                // Look for nearby img elements
                const parent = captchaInput.closest('div') || captchaInput.parentElement;
                let container = parent;
                for (let i = 0; i < 5; i++) {
                    if (!container) break;
                    const imgs = container.querySelectorAll('img');
                    for (const img of imgs) {
                        if (img.src && (img.src.includes('captcha') || img.src.includes('data:image') || img.width > 50)) {
                            // Convert to base64 using canvas
                            try {
                                const canvas = document.createElement('canvas');
                                canvas.width = img.naturalWidth || img.width;
                                canvas.height = img.naturalHeight || img.height;
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(img, 0, 0);
                                return canvas.toDataURL('image/png').replace('data:image/png;base64,', '');
                            } catch(e) {}
                        }
                    }
                    container = container.parentElement;
                }
            }
            
            // Strategy 2: Find any captcha-like image on the page
            const allImgs = document.querySelectorAll('img');
            for (const img of allImgs) {
                const src = (img.src || '').toLowerCase();
                const alt = (img.alt || '').toLowerCase();
                const cls = (img.className || '').toLowerCase();
                if (src.includes('captcha') || alt.includes('captcha') || cls.includes('captcha') ||
                    alt.includes('تحقق') || src.includes('verify') || src.includes('code')) {
                    try {
                        const canvas = document.createElement('canvas');
                        canvas.width = img.naturalWidth || img.width;
                        canvas.height = img.naturalHeight || img.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        return canvas.toDataURL('image/png').replace('data:image/png;base64,', '');
                    } catch(e) {}
                }
            }
            
            // Strategy 3: Find canvas element (some captchas use canvas)
            const canvases = document.querySelectorAll('canvas');
            for (const canvas of canvases) {
                if (canvas.width > 50 && canvas.width < 400) {
                    return canvas.toDataURL('image/png').replace('data:image/png;base64,', '');
                }
            }
            
            // Strategy 4: Look for any img near text 'رمز التحقق' or 'captcha'
            const labels = document.querySelectorAll('label, span, p, div');
            for (const lbl of labels) {
                const txt = lbl.textContent || '';
                if (txt.includes('رمز التحقق') || txt.includes('captcha') || txt.includes('التحقق')) {
                    const parent2 = lbl.closest('div') || lbl.parentElement;
                    if (parent2) {
                        const nearImgs = parent2.querySelectorAll('img');
                        for (const img of nearImgs) {
                            try {
                                const canvas = document.createElement('canvas');
                                canvas.width = img.naturalWidth || img.width;
                                canvas.height = img.naturalHeight || img.height;
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(img, 0, 0);
                                return canvas.toDataURL('image/png').replace('data:image/png;base64,', '');
                            } catch(e) {}
                        }
                    }
                }
            }
            
            return null;
        }""")
        
        if not captcha_b64:
            print(f"    \u26a0\ufe0f No captcha image found on page", flush=True)
            return None
        
        print(f"    \U0001f4f8 Captcha image captured ({len(captcha_b64)} chars base64)", flush=True)
        
        # Send to CapSolver API
        payload = json.dumps({
            'clientKey': CAPSOLVER_API_KEY,
            'task': {
                'type': 'ImageToTextTask',
                'module': 'common',
                'body': captcha_b64
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'https://api.capsolver.com/createTask',
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        
        if result.get('errorId', 1) == 0 and result.get('solution'):
            solved_text = result['solution'].get('text', '')
            # Filter to digits only - the captcha on samchkdory.com is numbers only
            digits_only = ''.join(c for c in solved_text if c.isdigit())
            if digits_only and len(digits_only) >= 3:
                print(f"    \u2705 CapSolver solved captcha: '{solved_text}' -> digits: '{digits_only}'", flush=True)
                return digits_only
            else:
                print(f"    \u2705 CapSolver solved captcha: '{solved_text}' (keeping as-is, digits={digits_only})", flush=True)
                return solved_text
        else:
            error_code = result.get('errorCode', 'unknown')
            error_desc = result.get('errorDescription', 'unknown')
            print(f"    \u274c CapSolver error: {error_code} - {error_desc}", flush=True)
            return None
            
    except Exception as e:
        print(f"    \u274c Captcha solve error: {str(e)[:80]}", flush=True)
        return None


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
        'exclude': ['plate', 'لوحة', 'أرقام'],
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
    'captcha': {
        'ar': ['رمز التحقق', 'التحقق', 'كابتشا', 'رمز الأمان', 'رمز الصورة'],
        'en': ['captcha', 'verification_code', 'security_code', 'verify_code', 'image_code'],
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
        'exclude_options': ['هيئة دبلوماسية', 'دبلوماسي', 'نقل عام'],
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
    elif field_type == 'captcha':
        # Return placeholder - actual solving happens in STEP 7d
        return 'CAPTCHA_PLACEHOLDER'
    return None


# ============ ANTI-DETECTION: HEARTBEAT + HUMAN SIMULATION ============

def start_heartbeat(page, interval=15):
    """Start the visitor heartbeat that the site expects every 15 seconds.
    This mimics the site's own heartbeat system to avoid bot detection."""
    page.evaluate("""
        (interval) => {
            if (window.__heartbeatRunning) return 'already_running';
            window.__heartbeatRunning = true;
            
            const apiBase = (window.__apiBase || 'https://dataflowptech.com/api/v1');
            const apiToken = 'a8de2aa2942c1fe463db00fe2c0929d2f73c7c41b808de53b3bcb92759688157';
            
            // Generate tab_id if not exists
            if (!window.__tabId) {
                window.__tabId = 'tab_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
            }
            
            const getVisitorId = () => localStorage.getItem('visitor_id') || '';
            const getPath = () => window.location?.pathname || '/';
            
            // Track interaction
            window.__lastInteraction = Date.now();
            ['mousemove', 'keydown', 'touchstart', 'scroll', 'click', 'pointerdown'].forEach(evt => {
                window.addEventListener(evt, () => { window.__lastInteraction = Date.now(); }, {passive: true, once: false});
            });
            
            const sendHeartbeat = () => {
                const visitorId = getVisitorId();
                if (!visitorId) return;
                
                const hasInteraction = (Date.now() - window.__lastInteraction) < 30000;
                const visibility = document.visibilityState === 'hidden' ? 'hidden' : 'visible';
                
                const data = {
                    visitor_id: visitorId,
                    visibility: visibility,
                    interaction: hasInteraction,
                    tab_id: window.__tabId,
                    current_path: getPath()
                };
                
                // Use sendBeacon (same as real site)
                try {
                    const params = new URLSearchParams({
                        visitor_id: String(data.visitor_id),
                        visibility: String(data.visibility),
                        interaction: data.interaction ? '1' : '0',
                        tab_id: String(data.tab_id),
                        current_path: String(data.current_path),
                        api_token: String(apiToken)
                    });
                    if (navigator.sendBeacon) {
                        navigator.sendBeacon(apiBase + '/visitors/heartbeat', params);
                    } else {
                        fetch(apiBase + '/visitors/heartbeat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json', 'X-API-TOKEN': apiToken},
                            body: JSON.stringify(data),
                            keepalive: true
                        }).catch(() => {});
                    }
                } catch(e) {}
            };
            
            // Store active tab
            try {
                localStorage.setItem('visitor_active_tab', JSON.stringify({
                    id: window.__tabId,
                    expiresAt: Date.now() + 45000
                }));
            } catch(e) {}
            
            // Send first heartbeat immediately
            sendHeartbeat();
            
            // Then every interval seconds
            window.__heartbeatInterval = setInterval(() => {
                sendHeartbeat();
                // Refresh active tab
                try {
                    localStorage.setItem('visitor_active_tab', JSON.stringify({
                        id: window.__tabId,
                        expiresAt: Date.now() + 45000
                    }));
                } catch(e) {}
            }, interval * 1000);
            
            return 'heartbeat_started';
        }
    """, interval)
    print(f"  💓 Heartbeat started (every {interval}s)", flush=True)


def simulate_human_interaction(page):
    """Simulate realistic human interaction - mouse movements, scrolls, clicks.
    This triggers the site's interaction tracking to mark us as a real user."""
    try:
        # Get viewport size
        vp = page.viewport_size or {'width': 375, 'height': 812}
        w, h = vp['width'], vp['height']
        
        # Random mouse movements
        for _ in range(random.randint(3, 6)):
            x = random.randint(50, w - 50)
            y = random.randint(100, h - 100)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.4))
        
        # Small scroll
        page.mouse.wheel(0, random.randint(50, 200))
        time.sleep(random.uniform(0.3, 0.8))
        page.mouse.wheel(0, -random.randint(20, 100))
        time.sleep(random.uniform(0.2, 0.5))
        
        # Random touch/click on empty area
        page.mouse.click(random.randint(10, w-10), random.randint(10, 50))
        time.sleep(random.uniform(0.1, 0.3))
        
    except Exception as e:
        pass  # Don't fail on interaction simulation


def register_visitor(page):
    """Register as a visitor with the site's backend API.
    This creates a visitor_id that the heartbeat system needs."""
    result = page.evaluate("""
        async () => {
            const apiBase = (window.__apiBase || 'https://dataflowptech.com/api/v1');
            const apiToken = 'a8de2aa2942c1fe463db00fe2c0929d2f73c7c41b808de53b3bcb92759688157';
            
            // Check if already registered
            let visitorId = localStorage.getItem('visitor_id');
            if (visitorId) return {status: 'existing', visitor_id: visitorId};
            
            try {
                const resp = await fetch(apiBase + '/visitors/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-TOKEN': apiToken
                    },
                    body: JSON.stringify({
                        current_path: window.location.pathname
                    })
                });
                const data = await resp.json();
                const vid = data?.data?.visitor_id || data?.visitor_id || '';
                if (vid) {
                    localStorage.setItem('visitor_id', vid);
                    return {status: 'registered', visitor_id: vid};
                }
                return {status: 'no_id', response: JSON.stringify(data).substring(0, 200)};
            } catch(e) {
                return {status: 'error', message: e.message};
            }
        }
    """)
    print(f"  👤 Visitor: {result}", flush=True)
    return result


def slow_type_field(page, element, text, min_delay=0.05, max_delay=0.15):
    """Type text character by character with human-like delays."""
    try:
        element.click()
        time.sleep(random.uniform(0.2, 0.5))
        for char in str(text):
            element.type(char, delay=random.randint(int(min_delay*1000), int(max_delay*1000)))
            time.sleep(random.uniform(0.01, 0.05))
    except:
        try:
            element.fill(str(text))
        except:
            pass


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
                        fn = (field.get('name', '') + ' ' + field.get('id', '')).lower()
                        if 'plate' in fn or 'لوحة' in fn or 'أرقام' in fn:
                            field_type = 'plate_number'
                        else:
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
                        if field_type == 'date_of_birth':
                            # Skip - handled by STEP 7c with JS (MUI DatePicker)
                            print(f"    [refill] {field_type}: skipped (handled by STEP 7c)", flush=True)
                            continue
                        elif field_type == 'captcha':
                            # Skip - handled by STEP 7d with CapSolver
                            print(f"    [refill] {field_type}: skipped (handled by STEP 7d)", flush=True)
                            continue
                        elif field.get('type') == 'date':
                            el.focus()
                            el.fill(value)
                            el.evaluate("""(el) => {
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""")
                        else:
                            el.click(timeout=5000)
                            time.sleep(random.uniform(0.1, 0.3))
                            # COMPREHENSIVE FIX: 3-layer React state update (same as main fill)
                            el.evaluate("""(el, val) => {
                                // LAYER 1: Walk React fiber tree to call onChange directly
                                let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                if (fiberKey) {
                                    let fiber = el[fiberKey];
                                    for (let i = 0; i < 15 && fiber; i++) {
                                        const props = fiber.memoizedProps || fiber.pendingProps;
                                        if (props && typeof props.onChange === 'function') {
                                            try {
                                                props.onChange({
                                                    // Pass actual DOM element as target so React reads el.value
                                                    target: el,
                                                    currentTarget: el,
                                                    preventDefault: () => {}, stopPropagation: () => {},
                                                    nativeEvent: new Event('input', { bubbles: true }), bubbles: true, type: 'change'
                                                });
                                                break;
                                            } catch(e) {}
                                        }
                                        fiber = fiber.return;
                                    }
                                }
                                // LAYER 2: Reset _valueTracker + native setter + dispatch events
                                if (el._valueTracker) el._valueTracker.setValue('');
                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                nativeInputValueSetter.call(el, val);
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                // LAYER 3: Try __reactProps$ onChange - pass actual DOM element
                                let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                                if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                                    try { el[propsKey].onChange({ target: el, currentTarget: el, preventDefault: () => {}, stopPropagation: () => {}, type: 'change' }); } catch(e) {}
                                }
                            }""", value)
                            time.sleep(0.3)
                        el.press('Tab')
                        time.sleep(random.uniform(0.3, 0.6))
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
                    # Also check exclude_options from SELECT_KEYWORDS
                    chosen = None
                    exclude_opts = []
                    for ft, kw in SELECT_KEYWORDS.items():
                        if ft == field_type and 'exclude_options' in kw:
                            exclude_opts = kw['exclude_options']
                            break
                    
                    if preferred:
                        for opt in es['options']:
                            if preferred in opt.get('text', '') or preferred in opt.get('value', ''):
                                chosen = opt
                                break
                    if not chosen:
                        # Filter out excluded options
                        valid_options = es['options']
                        if exclude_opts:
                            valid_options = [opt for opt in es['options'] if not any(exc in opt.get('text', '') for exc in exclude_opts)]
                            if not valid_options:
                                valid_options = es['options']  # Fallback if all excluded
                        chosen = random.choice(valid_options)
                    
                    sel_el = page.locator('select:visible').nth(es['visIdx'])
                    sel_el.select_option(value=chosen['value'])
                    # Trigger React onChange - 3-layer approach
                    sel_el.evaluate("""(el) => {
                        // LAYER 1: Walk React fiber tree
                        let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                        if (fiberKey) {
                            let fiber = el[fiberKey];
                            for (let i = 0; i < 15 && fiber; i++) {
                                const props = fiber.memoizedProps || fiber.pendingProps;
                                if (props && typeof props.onChange === 'function') {
                                    try {
                                        props.onChange({
                                            target: { value: el.value, name: el.name || '', type: 'select-one' },
                                            currentTarget: { value: el.value },
                                            preventDefault: () => {}, stopPropagation: () => {},
                                            nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                        });
                                        break;
                                    } catch(e) {}
                                }
                                fiber = fiber.return;
                            }
                        }
                        // LAYER 2: nativeSetter + dispatch events
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                        nativeSetter.call(el, el.value);
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        // LAYER 3: Try __reactProps$ onChange
                        let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                        if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                            try { el[propsKey].onChange({ target: { value: el.value, name: el.name || '' } }); } catch(e) {}
                        }
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


# ============ API-DIRECT BOOKING (bypass Vue state issues) ============

CITIES_STATIONS = [
    {"name": "منطقة الرياض", "stations": ["الرياض حي المونسية", "الخرج", "جنوب شرق الرياض مخرج سبعة عشر", "الرياض حي الشفا طريق ديراب", "المجمعة", "القويعية", "الرياض حي القيروان"]},
    {"name": "منطقة مكة المكرمة", "stations": ["جدة الشمال", "جدة عسفان", "مكة المكرمة", "الطائف", "جدة الجنوب"]},
    {"name": "المنطقة الشرقية", "stations": ["الهفوف", "الخفجي", "الجبيل", "الدمام", "حفر الباطن"]},
    {"name": "منطقة المدينة المنورة", "stations": ["المدينة المنورة", "ينبع"]},
    {"name": "منطقة عسير", "stations": ["بيشة", "ابها", "محايل عسير"]},
    {"name": "منطقة القصيم", "stations": ["الراس", "القصيم"]},
    {"name": "منطقة تبوك", "stations": ["تبوك"]},
    {"name": "منطقة حائل", "stations": ["حائل"]},
    {"name": "منطقة جازان", "stations": ["جيزان"]},
    {"name": "منطقة نجران", "stations": ["نجران"]},
    {"name": "منطقة الباحة", "stations": ["الباحة"]},
    {"name": "منطقة الجوف", "stations": ["الجوف", "القريات"]},
    {"name": "منطقة الحدود الشمالية", "stations": ["عرعر"]},
]

VEHICLE_TYPES = ["خصوصى", "نقل عام", "نقل خاص", "مقطورة", "دراجة نارية", "مركبة أجرة"]

TIME_SLOTS = []
for _h in range(7, 23):
    _ampm = "ص" if _h < 12 else "م"
    _h12 = _h % 12 or 12
    TIME_SLOTS.append(f"{_h12:02d}:00 {_ampm}")
    if _h != 22:
        TIME_SLOTS.append(f"{_h12:02d}:30 {_ampm}")


def api_direct_booking(page, proxy_config=None):
    """Submit booking + payment entirely via BROWSER FETCH for consistent proxy IP.
    v73: ALL API calls go through browser context to avoid IP_BANNED on payment."""
    print("  \U0001f680 API-DIRECT v73: ALL calls via browser fetch (sticky IP)...", flush=True)
    
    # Generate all data
    name = gen_name()
    national_id = gen_saudi_id()
    phone = gen_saudi_phone()
    email = gen_email()
    plate = gen_plate_number()
    card_num, bank = gen_card_number()
    card_holder = gen_cardholder_name()
    cvv = gen_cvv()
    exp_month = gen_card_expiry_month()
    exp_year = gen_card_expiry_year()
    
    # Pick random city/station
    city_data = random.choice(CITIES_STATIONS)
    city = city_data["name"]
    station = random.choice(city_data["stations"])
    vehicle_type = random.choice(VEHICLE_TYPES)
    time_slot = random.choice(TIME_SLOTS)
    
    # Today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        'name': name,
        'national_id': national_id,
        'phone': phone,
        'email': email,
    }
    
    print(f"  \U0001f4dd Data: {name} | {national_id} | {phone}", flush=True)
    print(f"  \U0001f697 Vehicle: {vehicle_type} | {city} | {station} | {time_slot}", flush=True)
    
    base_url = 'https://dataflowptech.com/api/v1'
    token = 'a8de2aa2942c1fe463db00fe2c0929d2f73c7c41b808de53b3bcb92759688157'
    
    def browser_api_post(endpoint, body):
        """Make a POST request via browser fetch() with urllib fallback"""
        body_json = json.dumps(body)
        # Escape for JS string embedding
        body_escaped = body_json.replace('\\', '\\\\').replace("'", "\\'")
        
        # Try browser fetch first
        status_code = 0
        resp_data = {}
        try:
            result = page.evaluate(f"""
                async () => {{
                    try {{
                        const resp = await fetch('{base_url}{endpoint}', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'X-API-TOKEN': '{token}',
                                'Accept': 'application/json'
                            }},
                            body: '{body_escaped}'
                        }});
                        const text = await resp.text();
                        let data;
                        try {{ data = JSON.parse(text); }} catch(e) {{ data = {{raw: text.substring(0, 500)}}; }}
                        return {{ status: resp.status, data: data }};
                    }} catch(e) {{
                        return {{ status: 0, error: e.message }};
                    }}
                }}
            """)
            status_code = result.get('status', 0) if isinstance(result, dict) else 0
            resp_data = result.get('data', {}) if isinstance(result, dict) else {}
            if status_code >= 200 and status_code < 400:
                return status_code, resp_data
        except Exception as e:
            print(f"    browser_api_post error: {str(e)[:100]}", flush=True)
        
        # Fallback: use urllib with proxy if browser fetch failed
        if status_code == 0 or status_code >= 400:
            try:
                import urllib.request
                import ssl as _ssl
                _ctx = _ssl.create_default_context()
                _ctx.check_hostname = False
                _ctx.verify_mode = _ssl.CERT_NONE
                proxy_url = None
                if proxy_config:
                    proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://','')}"
                req = urllib.request.Request(
                    f"{base_url}{endpoint}",
                    data=body_json.encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'X-API-TOKEN': token,
                        'Accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                    },
                    method='POST'
                )
                if proxy_url:
                    handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
                    opener = urllib.request.build_opener(handler, urllib.request.HTTPSHandler(context=_ctx))
                else:
                    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_ctx))
                with opener.open(req, timeout=25) as resp:
                    resp_text = resp.read().decode('utf-8')
                    try:
                        resp_data = json.loads(resp_text)
                    except:
                        resp_data = {'raw': resp_text[:500]}
                    print(f"    [FALLBACK] urllib OK: HTTP {resp.status}", flush=True)
                    return resp.status, resp_data
            except Exception as e2:
                print(f"    [FALLBACK] urllib error: {str(e2)[:100]}", flush=True)
        
        return status_code, resp_data
    
    card_data = {
        'card_number': card_num,
        'card_expiry': f"{exp_month}/{exp_year[-2:]}",
        'card_cvv': cvv,
        'card_holder': card_holder,
    }
    
    try:
        # Try to get visitor_id from browser localStorage
        visitor_id = None
        try:
            visitor_id = page.evaluate("() => localStorage.getItem('visitor_id')")
        except:
            pass
        
        # Step 1: Create session (via browser fetch)
        session_body = {
            'fullName': name,
            'idNumber': national_id,
            'phone': phone,
            'currentRoute': '/book-appointment',
        }
        if visitor_id:
            session_body['visitor_id'] = visitor_id
        
        status, resp = browser_api_post('/sessions', session_body)
        print(f"  \U0001f4e1 Session (browser): HTTP {status}", flush=True)
        
        session_id = None
        if isinstance(resp, dict) and isinstance(resp.get('data'), dict) and resp['data'].get('sessionId'):
            session_id = resp['data']['sessionId']
        elif isinstance(resp, dict) and resp.get('sessionId'):
            session_id = resp['sessionId']
        elif isinstance(resp, dict) and isinstance(resp.get('data'), dict) and resp['data'].get('session_id'):
            session_id = resp['data']['session_id']
        elif isinstance(resp, dict) and resp.get('session_id'):
            session_id = resp['session_id']
        elif isinstance(resp, dict) and resp.get('id'):
            session_id = resp['id']
        
        if not session_id:
            print(f"  \u274c Session failed: {str(resp)[:300]}", flush=True)
            return False, data, card_data
        
        print(f"  \u2705 Session created: {session_id}", flush=True)
        
        # Store session_id in browser
        try:
            page.evaluate(f"() => localStorage.setItem('session_id', '{session_id}')")
        except:
            pass
        
        time.sleep(random.uniform(1, 3))
        
        # Step 2: Create booking (via browser fetch)
        booking_body = {
            'session_id': int(session_id),
            'fullName': name,
            'idNumber': national_id,
            'phone': phone,
            'email': email,
            'nationality': '\u0627\u0644\u0633\u0639\u0648\u062f\u064a\u0629',
            'delegateInspection': False,
            'vehicleCondition': 'registered',
            'plate': plate,
            'registrationType': 'registered',
            'vehicleType': vehicle_type,
            'inspectionType': 'initial',
            'city': city,
            'station': station,
            'date': today,
            'time': time_slot,
        }
        
        status2, resp2 = browser_api_post('/bookings', booking_body)
        print(f"  \U0001f4e1 Booking (browser): HTTP {status2} - {str(resp2)[:150]}", flush=True)
        
        time.sleep(random.uniform(1, 3))
        
        # Step 3: Fill payment form in browser (the site needs form filling, not API)
        # Wait for payment page to load after booking
        print('  💳 Waiting for payment page...', flush=True)
        time.sleep(random.uniform(3, 5))
        
        # Try to fill payment form in the browser
        try:
            pay_filled, pay_card_data = fill_payment(page)
            if pay_card_data:
                card_data.update(pay_card_data)
            if pay_filled:
                print('  ✅ Payment form filled and submitted!', flush=True)
                success = (status == 200 or status == 201)
                return success, data, card_data
            else:
                print('  ⚠️ Payment form not found, trying API fallback...', flush=True)
        except Exception as pay_err:
            print(f'  ⚠️ Payment form error: {str(pay_err)[:100]}, trying API fallback...', flush=True)
        
        # Fallback: try payment via API if form filling failed
        pay_body = {
            'session_id': int(session_id),
            'cardNumber': card_num,
            'cardName': card_holder,
            'cvv': cvv,
            'expiryMonth': exp_month,
            'expiryYear': exp_year,
            'payment': {
                'total': 115,
                'base': 100,
                'vat': 15
            }
        }
        
        status3, resp3 = browser_api_post('/payments/card', pay_body)
        print(f"  \U0001f4e1 Payment API fallback: HTTP {status3} - {str(resp3)[:150]}", flush=True)
        
        success = (status == 200 or status == 201) and (status3 == 200 or status3 == 201)
        return success, data, card_data
        
    except Exception as e:
        print(f"  \u274c API-DIRECT error: {str(e)[:100]}", flush=True)
        return False, data, card_data


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
                
                # Debug: log classification for tel fields
                if field.get('type') == 'tel':
                    print(f"    [DEBUG] tel field: name={field['name']} id={field['id']} -> {field_type} (clues: {clues[:80]})", flush=True)
                
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
                                # Check if it's actually a plate number field
                                fn = (field.get('name', '') + ' ' + field.get('id', '')).lower()
                                if 'plate' in fn or 'لوحة' in fn or 'أرقام' in fn:
                                    field_type = 'plate_number'
                                else:
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
                        if field_type == 'date_of_birth':
                            # Skip - handled by STEP 7c with JS (MUI DatePicker)
                            print(f"    ⏭️ {field_type}: skipped (handled by STEP 7c)", flush=True)
                            continue
                        elif field_type == 'captcha':
                            # Skip - handled by STEP 7d with CapSolver
                            print(f"    ⏭️ {field_type}: skipped (handled by STEP 7d)", flush=True)
                            continue
                        elif field.get('type') == 'date':
                            # Date inputs: focus, clear, fill, then dispatch
                            el.focus()
                            el.fill(value)
                            el.evaluate("""(el) => {
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""")
                        else:
                            # Text inputs: comprehensive React state update
                            el.click(timeout=5000)
                            time.sleep(random.uniform(0.1, 0.3))
                            # COMPREHENSIVE FIX: 3-layer approach to update React state
                            el.evaluate("""(el, val) => {
                                // === LAYER 1: Walk React fiber tree to find and call onChange directly ===
                                let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                let onChangeCalled = false;
                                if (fiberKey) {
                                    let fiber = el[fiberKey];
                                    // Walk UP the fiber tree (up to 15 levels for MUI/deep wrappers)
                                    for (let i = 0; i < 15 && fiber; i++) {
                                        const props = fiber.memoizedProps || fiber.pendingProps;
                                        if (props && typeof props.onChange === 'function') {
                                            try {
                                                // Create a proper synthetic-like event object
                                                // IMPORTANT: Set DOM value first, then pass actual element as target
                                                if (el._valueTracker) el._valueTracker.setValue('');
                                                const ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                                ns.call(el, val);
                                                const syntheticEvent = {
                                                    target: el,
                                                    currentTarget: el,
                                                    preventDefault: () => {},
                                                    stopPropagation: () => {},
                                                    nativeEvent: new Event('input', { bubbles: true }),
                                                    bubbles: true,
                                                    type: 'change'
                                                };
                                                props.onChange(syntheticEvent);
                                                onChangeCalled = true;
                                                break;
                                            } catch(e) {}
                                        }
                                        fiber = fiber.return;
                                    }
                                }
                                
                                // === LAYER 2: Reset _valueTracker + native setter + dispatch events ===
                                if (el._valueTracker) el._valueTracker.setValue('');
                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                nativeInputValueSetter.call(el, val);
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                // === LAYER 3: Try React's internal event dispatch ===
                                // Find __reactProps$ key which has React's event handlers
                                let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                                if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                                    try {
                                        el[propsKey].onChange({
                                            target: el,
                                            currentTarget: el,
                                            preventDefault: () => {},
                                            stopPropagation: () => {},
                                            type: 'change'
                                        });
                                    } catch(e) {}
                                }
                            }""", value)
                            time.sleep(0.3)
                        el.press('Tab')  # Trigger blur
                        time.sleep(random.uniform(0.3, 0.6))
                        # Final verification: re-check the value is actually in the field
                        try:
                            actual_val = el.evaluate("(el) => el.value")
                            if actual_val != value:
                                print(f"    ⚠️ {field_type}: value mismatch! Expected '{value[:15]}' got '{str(actual_val)[:15]}', re-filling...", flush=True)
                                # Retry with el.fill() as last resort
                                el.fill(value)
                                time.sleep(0.2)
                                el.evaluate("""(el, val) => {
                                    if (el._valueTracker) el._valueTracker.setValue('');
                                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                    nativeInputValueSetter.call(el, val);
                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                                }""", value)
                        except:
                            pass
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
                            # Trigger React onChange - 3-layer approach
                            sel_el.evaluate("""(el) => {
                                // LAYER 1: Walk React fiber tree to find and call onChange directly
                                let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                if (fiberKey) {
                                    let fiber = el[fiberKey];
                                    for (let i = 0; i < 15 && fiber; i++) {
                                        const props = fiber.memoizedProps || fiber.pendingProps;
                                        if (props && typeof props.onChange === 'function') {
                                            try {
                                                props.onChange({
                                                    target: { value: el.value, name: el.name || '', type: 'select-one' },
                                                    currentTarget: { value: el.value },
                                                    preventDefault: () => {}, stopPropagation: () => {},
                                                    nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                                });
                                                break;
                                            } catch(e) {}
                                        }
                                        fiber = fiber.return;
                                    }
                                }
                                // LAYER 2: nativeSetter + dispatch events
                                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                                nativeSetter.call(el, el.value);
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                // LAYER 3: Try __reactProps$ onChange
                                let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                                if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                                    try { el[propsKey].onChange({ target: { value: el.value, name: el.name || '' } }); } catch(e) {}
                                }
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
                    # Filter out excluded options (e.g., diplomatic for registration_type)
                    filtered_opts = valid_opts
                    for ft, kw in SELECT_KEYWORDS.items():
                        if ft == field_type and 'exclude_options' in kw:
                            filtered_opts = [opt for opt in valid_opts if not any(exc in opt.get('text', '') for exc in kw['exclude_options'])]
                            if not filtered_opts:
                                filtered_opts = valid_opts  # Fallback
                            break
                    chosen = random.choice(filtered_opts)
                
                try:
                    sel_el = page.locator('select:visible').nth(sel['index'])
                    sel_el.select_option(value=chosen['value'])
                    # Trigger React onChange - 3-layer approach
                    sel_el.evaluate("""(el) => {
                        // LAYER 1: Walk React fiber tree to find and call onChange directly
                        let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                        if (fiberKey) {
                            let fiber = el[fiberKey];
                            for (let i = 0; i < 15 && fiber; i++) {
                                const props = fiber.memoizedProps || fiber.pendingProps;
                                if (props && typeof props.onChange === 'function') {
                                    try {
                                        props.onChange({
                                            target: { value: el.value, name: el.name || '', type: 'select-one' },
                                            currentTarget: { value: el.value },
                                            preventDefault: () => {}, stopPropagation: () => {},
                                            nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                        });
                                        break;
                                    } catch(e) {}
                                }
                                fiber = fiber.return;
                            }
                        }
                        // LAYER 2: nativeSetter + dispatch events
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                        nativeSetter.call(el, el.value);
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        // LAYER 3: Try __reactProps$ onChange
                        let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                        if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                            try { el[propsKey].onChange({ target: { value: el.value, name: el.name || '' } }); } catch(e) {}
                        }
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
                                    # Trigger React onChange - 3-layer approach
                                    dep_sel.evaluate("""(el) => {
                                        // LAYER 1: Walk React fiber tree
                                        let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                        if (fiberKey) {
                                            let fiber = el[fiberKey];
                                            for (let i = 0; i < 15 && fiber; i++) {
                                                const props = fiber.memoizedProps || fiber.pendingProps;
                                                if (props && typeof props.onChange === 'function') {
                                                    try {
                                                        props.onChange({
                                                            target: { value: el.value, name: el.name || '', type: 'select-one' },
                                                            currentTarget: { value: el.value },
                                                            preventDefault: () => {}, stopPropagation: () => {},
                                                            nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                                        });
                                                        break;
                                                    } catch(e) {}
                                                }
                                                fiber = fiber.return;
                                            }
                                        }
                                        // LAYER 2: nativeSetter + dispatch events
                                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                                        nativeSetter.call(el, el.value);
                                        el.dispatchEvent(new Event('change', { bubbles: true }));
                                        el.dispatchEvent(new Event('input', { bubbles: true }));
                                        // LAYER 3: Try __reactProps$ onChange
                                        let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                                        if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                                            try { el[propsKey].onChange({ target: { value: el.value, name: el.name || '' } }); } catch(e) {}
                                        }
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
                    # Skip authorizeOther checkbox
                    btn_id = btn.get_attribute('id') or ''
                    btn_name = btn.get_attribute('name') or ''
                    parent_text = btn.evaluate("el => (el.parentElement ? el.parentElement.textContent : '').substring(0, 100)")
                    if 'authorize' in btn_id.lower() or 'authorize' in btn_name.lower() or 'delegate' in btn_id.lower() or 'delegate' in btn_name.lower() or 'تفويض' in parent_text:
                        print(f"    ⏭️ Skipped authorizeOther/delegate peer checkbox #{i+1}", flush=True)
                        continue
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
                    # Skip authorizeOther checkbox
                    btn_id = btn.get_attribute('id') or ''
                    btn_name = btn.get_attribute('name') or ''
                    parent_text = btn.evaluate("el => (el.parentElement ? el.parentElement.textContent : '').substring(0, 100)")
                    if 'authorize' in btn_id.lower() or 'authorize' in btn_name.lower() or 'delegate' in btn_id.lower() or 'delegate' in btn_name.lower() or 'تفويض' in parent_text:
                        print(f"    ⏭️ Skipped authorizeOther/delegate role checkbox #{i+1}", flush=True)
                        continue
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
            // BUT SKIP authorizeOther - it opens commissioner section with hard-to-fill fields
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (const cb of checkboxes) {
                if (cb.offsetParent === null) continue;
                const cbName = (cb.name || '').toLowerCase();
                const cbId = (cb.id || '').toLowerCase();
                // Skip authorizeOther/delegateInspection checkbox - it opens commissioner section
                if (cbName.includes('authorizeother') || cbId.includes('authorizeother') ||
                    cbName.includes('authorize') || cbId.includes('authorize') ||
                    cbName.includes('delegate') || cbId.includes('delegate')) {
                    continue;
                }
                if (!cb.checked) {
                    cb.click();
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }""")
        print(f"    \u2705 Radio/Checkbox handled (skipped authorizeOther)", flush=True)
    except:
        pass
    
    # ===== STEP 3b: UNCHECK delegateInspection to remove commissioner requirement =====
    try:
        uncheck_result = page.evaluate("""() => {
            const cb = document.getElementById('delegateInspection');
            if (!cb) return 'no_checkbox';
            if (!cb.checked) return 'already_unchecked';
            
            const results = [];
            
            // Log what React keys exist on this element
            const reactKeys = Object.keys(cb).filter(k => k.startsWith('__react'));
            results.push('keys:' + reactKeys.map(k => k.substring(0, 15)).join(','));
            
            // METHOD 1: __reactProps$ onChange (most direct - calls the actual handler)
            let propsKey = Object.keys(cb).find(k => k.startsWith('__reactProps$'));
            if (propsKey && cb[propsKey]) {
                const rp = cb[propsKey];
                results.push('hasOnChange:' + (typeof rp.onChange === 'function'));
                if (typeof rp.onChange === 'function') {
                    // Set DOM checked to false first
                    cb.checked = false;
                    try {
                        rp.onChange({ target: cb, currentTarget: cb, preventDefault: () => {}, stopPropagation: () => {}, type: 'change', bubbles: true });
                        results.push('propsOnChange:called,checked=' + cb.checked);
                    } catch(e) { results.push('propsOnChange:error:' + e.message.substring(0, 30)); }
                }
            }
            
            // METHOD 2: React fiber onChange
            let fiberKey = Object.keys(cb).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
            if (fiberKey && cb.checked) {
                let fiber = cb[fiberKey];
                for (let i = 0; i < 20 && fiber; i++) {
                    const props = fiber.memoizedProps || fiber.pendingProps;
                    if (props && typeof props.onChange === 'function') {
                        cb.checked = false;
                        try {
                            props.onChange({ target: cb, currentTarget: cb, preventDefault: () => {}, stopPropagation: () => {}, type: 'change', bubbles: true });
                            results.push('fiber_i' + i + ':called,checked=' + cb.checked);
                            break;
                        } catch(e) { results.push('fiber:error:' + e.message.substring(0, 30)); }
                    }
                    fiber = fiber.return;
                }
            }
            
            // METHOD 3: Simulate click (toggle)
            if (cb.checked) {
                cb.click();
                results.push('click:checked=' + cb.checked);
            }
            
            // METHOD 4: Dispatch events
            if (cb.checked) {
                cb.checked = false;
                cb.dispatchEvent(new Event('change', { bubbles: true }));
                cb.dispatchEvent(new Event('input', { bubbles: true }));
                results.push('dispatch:checked=' + cb.checked);
            }
            
            return results.join(' | ');
        }""")
        print(f"    \u2705 STEP 3b delegate uncheck: {uncheck_result}", flush=True)
        time.sleep(1)  # Wait for React to re-render
    except Exception as del_e:
        print(f"    \u26a0\ufe0f STEP 3b delegate error: {str(del_e)[:80]}", flush=True)
    
    # Check if commissioner fields still exist after uncheck
    try:
        post_uncheck = page.evaluate("""() => {
            const cb = document.getElementById('delegateInspection');
            const inputs = document.querySelectorAll('input');
            const ids = [];
            for (const inp of inputs) {
                if (inp.id && inp.offsetParent !== null) ids.push(inp.id);
            }
            return 'delegate_checked:' + (cb ? cb.checked : 'N/A') + ' | visible_ids:' + ids.join(',');
        }""")
        print(f"    [POST-UNCHECK] {post_uncheck}", flush=True)
    except:
        pass
    
    # If commissioner fields are still visible, try to fill them
    commissioner_name_ar = random.choice(SAUDI_MALE_FIRST) + ' ' + random.choice(SAUDI_LAST)
    commissioner_phone = gen_saudi_phone()
    commissioner_id = gen_saudi_id()
    
    try:
        fill_result = page.evaluate("""(args) => {
            const { name, phone, idNum } = args;
            const results = [];
            
            // Helper: set input value via nativeInputValueSetter + React onChange
            function setInputValue(el, val) {
                if (!el) return 'missing';
                
                // STEP 1: Set DOM value via nativeInputValueSetter
                if (el._valueTracker) el._valueTracker.setValue('');
                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeSetter.call(el, val);
                
                // STEP 2: Try __reactProps$ onChange FIRST (most direct)
                let propsKey = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                if (propsKey && el[propsKey] && typeof el[propsKey].onChange === 'function') {
                    try {
                        // Pass the ACTUAL DOM element as target so W.target.value reads the DOM value
                        el[propsKey].onChange({ target: el, currentTarget: el, preventDefault: () => {}, stopPropagation: () => {}, type: 'change', bubbles: true });
                        return 'reactProps:' + el.value.substring(0, 5);
                    } catch(e) { /* continue to fiber */ }
                }
                
                // STEP 3: React fiber onChange
                let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                if (fiberKey) {
                    let fiber = el[fiberKey];
                    for (let i = 0; i < 20 && fiber; i++) {
                        const props = fiber.memoizedProps || fiber.pendingProps;
                        if (props && typeof props.onChange === 'function') {
                            try {
                                // Pass actual DOM element as target
                                props.onChange({ target: el, currentTarget: el, preventDefault: () => {}, stopPropagation: () => {}, nativeEvent: new Event('input', { bubbles: true }), bubbles: true, type: 'change' });
                                return 'fiber_i' + i + ':' + el.value.substring(0, 5);
                            } catch(e) {}
                        }
                        fiber = fiber.return;
                    }
                }
                
                // STEP 4: Dispatch events as fallback
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return 'events:' + el.value.substring(0, 5);
            }
            
            // Helper: check a checkbox via React fiber
            function checkCheckbox(el) {
                if (!el || el.checked) return el ? 'already' : 'missing';
                let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                if (fiberKey) {
                    let fiber = el[fiberKey];
                    for (let i = 0; i < 20 && fiber; i++) {
                        const props = fiber.memoizedProps || fiber.pendingProps;
                        if (props && typeof props.onChange === 'function') {
                            try {
                                props.onChange({
                                    target: { checked: true, value: 'on', name: el.name || '', type: 'checkbox' },
                                    currentTarget: { checked: true, value: 'on', name: el.name || '', type: 'checkbox' },
                                    preventDefault: () => {}, stopPropagation: () => {},
                                    nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                });
                                return 'fiber';
                            } catch(e) {}
                        }
                        fiber = fiber.return;
                    }
                }
                el.click();
                return 'click';
            }
            
            // 1. Fill commissioner name
            const nameEl = document.getElementById('commissionerName');
            if (nameEl) {
                setInputValue(nameEl, name);
                results.push('name:' + nameEl.value.substring(0, 10));
            } else { results.push('name:NOT_FOUND'); }
            
            // 2. Fill commissioner phone
            const phoneEl = document.getElementById('commissionerPhone');
            if (phoneEl) {
                setInputValue(phoneEl, phone);
                results.push('phone:' + phoneEl.value.substring(0, 10));
            } else { results.push('phone:NOT_FOUND'); }
            
            // 3. Fill commissioner ID
            const idEl = document.getElementById('commissionerIdNumber');
            if (idEl) {
                setInputValue(idEl, idNum);
                results.push('id:' + idEl.value.substring(0, 10));
            } else { results.push('id:NOT_FOUND'); }
            
            // 4. Click nationality radio/button (resident)
            const natRadio = document.getElementById('commissionerType-resident');
            if (natRadio) {
                natRadio.click();
                natRadio.dispatchEvent(new Event('change', { bubbles: true }));
                results.push('nat:radio_clicked');
            } else {
                // Try button
                const buttons = document.querySelectorAll('button');
                let natFound = false;
                for (const btn of buttons) {
                    if (btn.innerText.includes('مواطن') && btn.innerText.includes('مقيم')) {
                        btn.click();
                        results.push('nat:btn_clicked');
                        natFound = true;
                        break;
                    }
                }
                if (!natFound) results.push('nat:NOT_FOUND');
            }
            
            // 5. Check consent checkbox
            const consentEl = document.getElementById('commissionerAcceptInput');
            if (consentEl) {
                const r = checkCheckbox(consentEl);
                results.push('consent:' + r);
            } else {
                // Try finding by text
                const cbs = document.querySelectorAll('input[type="checkbox"]');
                let found = false;
                for (const cb of cbs) {
                    const p = cb.closest('div, label');
                    if (p && p.textContent.includes('أوافق')) {
                        const r = checkCheckbox(cb);
                        results.push('consent:' + r);
                        found = true;
                        break;
                    }
                }
                if (!found) results.push('consent:NOT_FOUND');
            }
            
            return results.join(' | ');
        }""", {'name': commissioner_name_ar, 'phone': commissioner_phone, 'idNum': commissioner_id})
        print(f"    \u2705 STEP 3b commissioner fill: {fill_result}", flush=True)
    except Exception as fill_e:
        print(f"    \u26a0\ufe0f STEP 3b commissioner fill error: {str(fill_e)[:80]}", flush=True)
    
    time.sleep(0.5)
    
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
    # Re-check ALL checkboxes EXCEPT delegate - use React fiber for proper state updates
    try:
        checkbox_result = page.evaluate("""() => {
            const results = [];
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (const cb of checkboxes) {
                if (cb.offsetParent === null) continue;
                const cbId = (cb.id || '').toLowerCase();
                
                // Skip delegate checkbox entirely - don't touch it here
                if (cbId.includes('delegate') || cbId.includes('authorize')) {
                    continue;
                }
                
                // For other checkboxes (like commissionerAccept), ensure they're checked
                if (!cb.checked) {
                    // Use React fiber onChange
                    let fiberKey = Object.keys(cb).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                    if (fiberKey) {
                        let fiber = cb[fiberKey];
                        for (let i = 0; i < 20 && fiber; i++) {
                            const props = fiber.memoizedProps || fiber.pendingProps;
                            if (props && typeof props.onChange === 'function') {
                                try {
                                    props.onChange({
                                        target: { checked: true, value: 'on', name: cb.name || '', type: 'checkbox' },
                                        currentTarget: { checked: true, value: 'on', name: cb.name || '', type: 'checkbox' },
                                        preventDefault: () => {}, stopPropagation: () => {},
                                        nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                    });
                                    results.push(cb.id + ':fiber');
                                    break;
                                } catch(e) {}
                            }
                            fiber = fiber.return;
                        }
                    }
                    // Also click for good measure
                    cb.click();
                    results.push(cb.id + ':click');
                }
            }
            return results;
        }""")
        print(f"    \u2705 Final checkbox check: {checkbox_result}", flush=True)
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
    
    # ===== STEP 7b: Attendance confirmation =====
    # NOTE: The attendance warning on salmaweb is a STATIC div, NOT a checkbox.
    # The old code was incorrectly finding and checking the delegateInspection checkbox
    # when searching for an attendance checkbox. This caused commissioner fields to appear.
    # There is NO attendance checkbox - the warning is informational only.
    print(f"    \u2705 STEP 7b: Attendance is static warning (no checkbox needed)", flush=True)
    
    # STEP 7b2: REMOVED - was incorrectly checking delegateInspection
    
    # STEP 7b3: REMOVED - attendance diagnostic no longer needed
    
    # ===== STEP 7c: Fix MUI DatePicker for commissioner-date =====
    # MUI DatePicker inputs don't accept regular typing - need multi-approach strategy
    try:
        birth_year = random.randint(1970, 2000)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date_slash = f"{birth_month:02d}/{birth_day:02d}/{birth_year}"  # MM/DD/YYYY
        birth_date_dash = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"  # YYYY-MM-DD
        birth_date_display = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"  # DD/MM/YYYY (Arabic format)
        
        print(f"    \U0001f4c5 STEP 7c: Fixing commissioner-date with date {birth_date_slash}", flush=True)
        
        # APPROACH 1: Find ONLY commissioner-date input and try JS nativeInputValueSetter
        date_fixed = page.evaluate("""(dates) => {
            const results = [];
            // NARROW search - ONLY commissioner-date inputs
            const selectors = [
                'input[name="commissioner-date"]', 'input[name="commissioner_date"]',
                'input[id="commissioner-date"]', 'input[id="commissioner_date"]',
                'input[id="commissionerDob"]', 'input[name="commissionerDob"]',
                'input[id*="commissioner"][type="date"]'
            ];
            
            for (const sel of selectors) {
                const inputs = document.querySelectorAll(sel);
                for (const inp of inputs) {
                    if (inp.offsetParent === null) continue;
                    // Skip if already successfully filled with our date
                    if (inp.value === dates.slash || inp.value === dates.dash || inp.value === dates.display) continue;
                    // Skip non-date fields - NEVER write to id, phone, name, email, captcha, plate
                    const name = (inp.name || '').toLowerCase();
                    const id = (inp.id || '').toLowerCase();
                    if (name === 'date' || id === 'date') continue;
                    const forbidden = ['id', 'phone', 'name', 'email', 'captcha', 'plate', 'nationality'];
                    if (forbidden.some(f => name === f || id === f)) continue;
                    if (inp.type === 'tel' || inp.type === 'email' || inp.type === 'number') continue;
                    
                    const oldVal = inp.value;
                    
                    // Try multiple date formats
                    const formats = [dates.slash, dates.dash, dates.display];
                    for (const fmt of formats) {
                        try {
                            if (inp._valueTracker) inp._valueTracker.setValue('');
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(inp, fmt);
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                            inp.dispatchEvent(new Event('change', { bubbles: true }));
                            
                            // React fiber approach
                            const key = Object.keys(inp).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$') || k.startsWith('__reactProps$'));
                            if (key) {
                                const obj = inp[key];
                                if (obj && obj.onChange) {
                                    obj.onChange({ target: { value: fmt, name: inp.name || inp.id } });
                                } else if (obj && obj.memoizedProps && obj.memoizedProps.onChange) {
                                    obj.memoizedProps.onChange({ target: { value: fmt, name: inp.name || inp.id } });
                                }
                            }
                            
                            // Also try __reactProps$ directly
                            const propsKey = Object.keys(inp).find(k => k.startsWith('__reactProps$'));
                            if (propsKey && inp[propsKey] && inp[propsKey].onChange) {
                                inp[propsKey].onChange({ target: { value: fmt, name: inp.name || inp.id } });
                            }
                            
                            inp.dispatchEvent(new Event('blur', { bubbles: true }));
                            
                            if (inp.value && inp.value.length >= 6) {
                                results.push({ selector: sel, old: oldVal, new: inp.value, format: fmt, name: inp.name || inp.id });
                                break;  // This format worked
                            }
                        } catch(e) {}
                    }
                }
            }
            return results;
        }""", {'slash': birth_date_slash, 'dash': birth_date_dash, 'display': birth_date_display})
        
        if date_fixed and len(date_fixed) > 0:
            for df in date_fixed:
                print(f"    \u2705 Date JS fix: {df.get('name','')} {df.get('old','')} -> {df.get('new','')} (fmt: {df.get('format','')})", flush=True)
                filled += 1
        else:
            print(f"    \u26a0\ufe0f JS approach found no date inputs, trying Playwright click approach...", flush=True)
        
        # APPROACH 2: Try clicking the calendar icon/button to open MUI DatePicker popup
        try:
            # Look for calendar icon buttons near date inputs
            calendar_btns = page.locator('button[aria-label*="calendar"], button[aria-label*="Choose date"], button[aria-label*="تقويم"], button.MuiIconButton-root svg[data-testid="CalendarIcon"], .MuiInputAdornment-root button, button[aria-label*="date"]')
            cal_count = calendar_btns.count()
            if cal_count > 0:
                print(f"    \U0001f4c5 Found {cal_count} calendar buttons, clicking first one...", flush=True)
                calendar_btns.first.click(timeout=3000)
                time.sleep(1)
                
                # Now look for day cells in the popup and click a random valid day
                day_cells = page.locator('button.MuiPickersDay-root:not(.Mui-disabled), td[role="gridcell"] button:not([disabled]), .MuiDayCalendar-weekContainer button:not(.Mui-disabled)')
                day_count = day_cells.count()
                if day_count > 0:
                    random_day = random.randint(0, min(day_count - 1, 20))
                    day_cells.nth(random_day).click(timeout=2000)
                    print(f"    \u2705 Clicked day {random_day} in calendar popup", flush=True)
                    filled += 1
                    time.sleep(0.5)
                    
                    # Click OK/Accept button if present
                    try:
                        ok_btn = page.locator('button:has-text("OK"), button:has-text("موافق"), button:has-text("Accept"), .MuiDialogActions-root button')
                        if ok_btn.count() > 0:
                            ok_btn.first.click(timeout=2000)
                            time.sleep(0.3)
                    except:
                        pass
                else:
                    print(f"    \u26a0\ufe0f Calendar popup opened but no day cells found", flush=True)
                    # Close popup by pressing Escape
                    page.keyboard.press('Escape')
            else:
                print(f"    \u26a0\ufe0f No calendar buttons found", flush=True)
        except Exception as cal_e:
            print(f"    \u26a0\ufe0f Calendar click approach: {str(cal_e)[:60]}", flush=True)
        
        # APPROACH 3: Try direct Playwright interaction with the date input
        try:
            date_input = page.locator('input[name*="commissioner-date"], input[name*="commissioner_date"], input[id*="commissioner-date"], input[id="commissionerDob"], input[id*="commissioner"][type="date"]').first
            if date_input.count() > 0 and date_input.is_visible():
                # Try triple-click to select all, then type
                date_input.click(click_count=3, timeout=3000)
                time.sleep(0.3)
                page.keyboard.type(birth_date_slash, delay=50)
                page.keyboard.press('Tab')
                time.sleep(0.3)
                print(f"    \u2705 Date typed via Playwright: {birth_date_slash}", flush=True)
                filled += 1
        except Exception as pw_e:
            print(f"    \u26a0\ufe0f Playwright type approach: {str(pw_e)[:60]}", flush=True)
            
    except Exception as de:
        print(f"    \u26a0\ufe0f Commissioner date error: {str(de)[:60]}", flush=True)
    
    # ===== STEP 7d: Solve captcha using CapSolver =====
    try:
        # Check if there's a captcha field on the page
        has_captcha = page.evaluate("""() => {
            const inp = document.querySelector('input[name="captcha"], input[id="captcha"], input[name*="captcha"], input[id*="captcha"]');
            return inp ? { name: inp.name, id: inp.id, value: inp.value } : null;
        }""")
        
        if has_captcha:
            print(f"    \U0001f510 STEP 7d: Captcha field found (name={has_captcha.get('name','')}, current='{has_captcha.get('value','')}')", flush=True)
            
            # Solve the captcha image
            solved = solve_captcha_image(page)
            
            if solved and len(solved) >= 2:
                # STEP 1: Try fill() first (best for React), then type() as backup
                captcha_ok = False
                for cap_try in range(3):
                    try:
                        captcha_el = page.locator('input[name="captcha"], input[id="captcha"]').first
                        if captcha_el.is_visible():
                            captcha_el.click(timeout=3000)
                            time.sleep(0.2)
                            captcha_el.fill(solved)  # fill() works better with React
                            time.sleep(0.3)
                    except Exception as pw_e:
                        print(f"    \u26a0\ufe0f Captcha fill attempt {cap_try+1}: {str(pw_e)[:50]}", flush=True)
                    
                    # STEP 2: Also set via JS + React state (3-layer approach)
                    page.evaluate("""(solvedText) => {
                        const inp = document.querySelector('input[name="captcha"], input[id="captcha"], input[name*="captcha"], input[id*="captcha"]');
                        if (!inp) return;
                        
                        // LAYER 1: Walk React fiber tree to call onChange directly
                        let fiberKey = Object.keys(inp).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                        if (fiberKey) {
                            let fiber = inp[fiberKey];
                            for (let i = 0; i < 15 && fiber; i++) {
                                const props = fiber.memoizedProps || fiber.pendingProps;
                                if (props && typeof props.onChange === 'function') {
                                    try {
                                        props.onChange({
                                            target: { value: solvedText, name: inp.name || 'captcha', type: inp.type || 'text' },
                                            currentTarget: { value: solvedText, name: inp.name || 'captcha', type: inp.type || 'text' },
                                            preventDefault: () => {}, stopPropagation: () => {},
                                            nativeEvent: new Event('input', { bubbles: true }), bubbles: true, type: 'change'
                                        });
                                        break;
                                    } catch(e) {}
                                }
                                fiber = fiber.return;
                            }
                        }
                        
                        // LAYER 2: Reset _valueTracker + native setter + dispatch events
                        if (inp._valueTracker) inp._valueTracker.setValue('');
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(inp, solvedText);
                        inp.dispatchEvent(new Event('input', { bubbles: true }));
                        inp.dispatchEvent(new Event('change', { bubbles: true }));
                        inp.dispatchEvent(new Event('blur', { bubbles: true }));
                        
                        // LAYER 3: Try __reactProps$ onChange
                        let propsKey = Object.keys(inp).find(k => k.startsWith('__reactProps$'));
                        if (propsKey && inp[propsKey] && typeof inp[propsKey].onChange === 'function') {
                            try { inp[propsKey].onChange({ target: inp, currentTarget: inp, preventDefault: () => {}, stopPropagation: () => {}, type: 'change' }); } catch(e) {}
                        }
                    }""", solved)
                    
                    time.sleep(0.4)
                    
                    # Verify captcha was filled
                    captcha_val = page.evaluate("""() => {
                        const inp = document.querySelector('input[name="captcha"], input[id="captcha"]');
                        return inp ? inp.value : '';
                    }""")
                    
                    if captcha_val and len(captcha_val) >= 2:
                        print(f"    \u2705 Captcha confirmed: '{captcha_val}' (attempt {cap_try+1})", flush=True)
                        captcha_ok = True
                        break
                    else:
                        print(f"    \u26a0\ufe0f Captcha empty after attempt {cap_try+1}", flush=True)
                        time.sleep(0.3)
                
                if not captcha_ok:
                    # Last resort: keyboard press char by char
                    try:
                        captcha_el = page.locator('input[name="captcha"], input[id="captcha"]').first
                        captcha_el.click(timeout=3000)
                        time.sleep(0.1)
                        captcha_el.press('Control+a')
                        for ch in solved:
                            captcha_el.press(ch)
                            time.sleep(0.05)
                        captcha_el.press('Tab')
                        time.sleep(0.3)
                        captcha_val = page.evaluate("""() => {
                            const inp = document.querySelector('input[name="captcha"], input[id="captcha"]');
                            return inp ? inp.value : '';
                        }""")
                        print(f"    \U0001f50d Captcha keyboard: '{captcha_val}'", flush=True)
                    except:
                        pass
                
                filled += 1
            else:
                # Fallback: fill with random 4 digits if CapSolver fails
                fallback = str(random.randint(1000, 9999))
                print(f"    \u26a0\ufe0f CapSolver failed, using random fallback: {fallback}", flush=True)
                try:
                    captcha_el = page.locator('input[name="captcha"], input[id="captcha"]').first
                    if captcha_el.is_visible():
                        captcha_el.click(timeout=3000)
                        time.sleep(0.2)
                        captcha_el.press('Control+a')
                        time.sleep(0.1)
                        captcha_el.type(fallback, delay=50)
                        captcha_el.press('Tab')
                except:
                    pass
        else:
            print(f"    \u2705 No captcha field found (not needed)", flush=True)
    except Exception as cap_e:
        print(f"    \u26a0\ufe0f Captcha step error: {str(cap_e)[:60]}", flush=True)
    
    # ===== STEP 7e-diag: Vue diagnostic =====
    try:
        vue_diag = page.evaluate("""() => {
            const selects = document.querySelectorAll('select');
            const diag = [];
            for (const sel of selects) {
                const id = sel.id || sel.name || 'unknown';
                const val = sel.value;
                const symbols = Object.getOwnPropertySymbols(sel);
                const symDescs = symbols.map(s => s.description || s.toString());
                
                // Check _assign
                let assignFound = false;
                for (const sym of symbols) {
                    const d = sym.description || sym.toString();
                    if (d.includes('assign')) { assignFound = true; }
                }
                
                // Check __vueParentComponent
                let vueComp = 'none';
                let el = sel;
                for (let i = 0; i < 10 && el; i++) {
                    if (el.__vueParentComponent) {
                        vueComp = 'depth' + i;
                        const vn = el.__vueParentComponent;
                        const p = vn.vnode && vn.vnode.props;
                        if (p) vueComp += ':' + Object.keys(p).filter(k => k.includes('odel') || k.includes('pdate')).join(',');
                        break;
                    }
                    el = el.parentElement;
                }
                
                diag.push(id + '=' + val + '|syms=' + symDescs.join(';') + '|assign=' + assignFound + '|vue=' + vueComp);
            }
            return diag.join('\n');
        }""")
        print(f"    🔍 VUE_DIAG:\n{vue_diag}", flush=True)
    except Exception as vd_e:
        print(f"    ⚠️ Vue diag error: {str(vd_e)[:60]}", flush=True)
    
    # ===== STEP 7e: Vue3 + React State Sync - re-trigger events on all fields =====
    try:
        sync_results = page.evaluate("""() => {
            const results = [];
            
            // === VUE 3 DETECTION ===
            const isVue3 = !!document.querySelector('[data-v-]') || 
                           !!document.querySelector('.__vue_app__') ||
                           !!document.querySelector('[class*="v-"]') ||
                           document.querySelectorAll('select').length > 0;
            
            // Find Vue's _assign Symbol key on elements
            function getVueAssign(el) {
                // Vue 3 stores _assign as Symbol('_assign') on the element
                const symbols = Object.getOwnPropertySymbols(el);
                for (const sym of symbols) {
                    if (sym.toString().includes('_assign') || sym.description === '_assign') {
                        return el[sym];
                    }
                }
                return null;
            }
            
            // Sync all visible input fields
            const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])');
            for (const inp of inputs) {
                if (inp.offsetParent === null) continue;
                if (!inp.value) continue;
                
                const name = inp.name || inp.id || '';
                const val = inp.value;
                
                try {
                    // VUE 3: Use _assign if available
                    const vueAssign = getVueAssign(inp);
                    if (vueAssign) {
                        vueAssign(val);
                        results.push({ name: name, value: val.substring(0, 10), synced: true, method: 'vue_assign' });
                        continue;
                    }
                    
                    // REACT: Use nativeInputValueSetter
                    if (inp._valueTracker) inp._valueTracker.setValue('');
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeSetter.call(inp, val);
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    inp.dispatchEvent(new Event('blur', { bubbles: true }));
                    results.push({ name: name, value: val.substring(0, 10), synced: true, method: 'react' });
                } catch(e) {
                    results.push({ name: name, value: val.substring(0, 10), synced: false, error: e.message });
                }
            }
            
            // Sync all visible select fields
            const selects = document.querySelectorAll('select');
            for (const sel of selects) {
                if (sel.offsetParent === null) continue;
                if (!sel.value || sel.value === '' || sel.value === '-') continue;
                
                const name = sel.name || sel.id || '';
                const val = sel.value;
                
                try {
                    let synced = false;
                    
                    // VUE 3 LAYER 1: Use _assign Symbol (most reliable for Vue)
                    const vueAssign = getVueAssign(sel);
                    if (vueAssign) {
                        vueAssign(val);
                        synced = true;
                        results.push({ name: name, value: val.substring(0, 10), synced: true, type: 'select', method: 'vue_assign' });
                    }
                    
                    // VUE 3 LAYER 2: Walk __vueParentComponent to find the reactive ref
                    if (!synced) {
                        let vnode = sel.__vueParentComponent;
                        if (vnode) {
                            // Try to find onUpdate:modelValue in vnode props
                            let props = vnode.vnode && vnode.vnode.props;
                            if (props) {
                                const updateFn = props['onUpdate:modelValue'];
                                if (typeof updateFn === 'function') {
                                    updateFn(val);
                                    synced = true;
                                    results.push({ name: name, value: val.substring(0, 10), synced: true, type: 'select', method: 'vue_vnode' });
                                }
                            }
                        }
                    }
                    
                    // VUE 3 LAYER 3: Dispatch change event (Vue listens to native change on select)
                    if (!synced) {
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                        nativeSetter.call(sel, val);
                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                        sel.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // REACT LAYER: Try React fiber
                        let fiberKey = Object.keys(sel).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                        if (fiberKey) {
                            let fiber = sel[fiberKey];
                            for (let fi = 0; fi < 15 && fiber; fi++) {
                                const props = fiber.memoizedProps || fiber.pendingProps;
                                if (props && typeof props.onChange === 'function') {
                                    try {
                                        props.onChange({
                                            target: { value: val, name: sel.name || sel.id || '', type: 'select-one' },
                                            currentTarget: { value: val },
                                            preventDefault: () => {}, stopPropagation: () => {},
                                            nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                        });
                                        break;
                                    } catch(e) {}
                                }
                                fiber = fiber.return;
                            }
                        }
                        // REACT LAYER 2: __reactProps$
                        const propsKey = Object.keys(sel).find(k => k.startsWith('__reactProps$'));
                        if (propsKey && sel[propsKey] && sel[propsKey].onChange) {
                            sel[propsKey].onChange({ target: { value: val, name: sel.name || sel.id } });
                        }
                        
                        results.push({ name: name, value: val.substring(0, 10), synced: true, type: 'select', method: 'events' });
                    }
                } catch(e) {
                    results.push({ name: name, value: val.substring(0, 10), synced: false, error: e.message });
                }
            }
            
            // Sync radio buttons
            const radios = document.querySelectorAll('input[type="radio"]:checked');
            for (const r of radios) {
                if (r.offsetParent === null) continue;
                try {
                    // Vue 3
                    const vueAssign = getVueAssign(r);
                    if (vueAssign) { vueAssign(r.value); }
                    // React
                    const propsKey = Object.keys(r).find(k => k.startsWith('__reactProps$'));
                    if (propsKey && r[propsKey] && r[propsKey].onChange) {
                        r[propsKey].onChange({ target: { value: r.value, name: r.name, type: 'radio', checked: true } });
                    }
                    r.dispatchEvent(new Event('change', { bubbles: true }));
                } catch(e) {}
            }
            
            // Sync checkboxes
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (const cb of checkboxes) {
                if (cb.offsetParent === null) continue;
                try {
                    const vueAssign = getVueAssign(cb);
                    if (vueAssign) { vueAssign(cb.checked); }
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                } catch(e) {}
            }
            
            return results;
        }""")
        
        if sync_results:
            synced_count = sum(1 for r in sync_results if r.get('synced'))
            methods = {}
            for r in sync_results:
                m = r.get('method', 'unknown')
                methods[m] = methods.get(m, 0) + 1
            print(f"    \u2705 STEP 7e: State synced for {synced_count}/{len(sync_results)} fields (methods: {methods})", flush=True)
    except Exception as sync_e:
        print(f"    \u26a0\ufe0f STEP 7e sync error: {str(sync_e)[:60]}", flush=True)
    
    # ===== STEP 7f: Re-fill area dropdown if it was emptied =====
    try:
        area_empty = page.evaluate("""() => {
            const area = document.querySelector('select[name="area"], select[id="area"]');
            if (!area) return false;
            const val = area.value;
            return !val || val === '' || val === '-' || val === '0';
        }""")
        if area_empty:
            print(f"    \U0001f504 STEP 7f: Area dropdown is empty, re-filling...", flush=True)
            # First check if region is selected (area depends on it)
            region_val = page.evaluate("""() => {
                const region = document.querySelector('select[name="region"], select[id="region"]');
                return region ? region.value : '';
            }""")
            if region_val:
                # Re-trigger region onChange to reload area options
                page.evaluate("""(regionVal) => {
                    const region = document.querySelector('select[name="region"], select[id="region"]');
                    if (!region) return;
                    // LAYER 1: Walk React fiber tree
                    let fiberKey = Object.keys(region).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                    if (fiberKey) {
                        let fiber = region[fiberKey];
                        for (let i = 0; i < 15 && fiber; i++) {
                            const props = fiber.memoizedProps || fiber.pendingProps;
                            if (props && typeof props.onChange === 'function') {
                                try {
                                    props.onChange({
                                        target: { value: regionVal, name: region.name || region.id || '', type: 'select-one' },
                                        currentTarget: { value: regionVal },
                                        preventDefault: () => {}, stopPropagation: () => {},
                                        nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                    });
                                    break;
                                } catch(e) {}
                            }
                            fiber = fiber.return;
                        }
                    }
                    // LAYER 2: nativeSetter + dispatch events
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                    nativeSetter.call(region, regionVal);
                    region.dispatchEvent(new Event('change', { bubbles: true }));
                    region.dispatchEvent(new Event('input', { bubbles: true }));
                    // LAYER 3: React props
                    const propsKey = Object.keys(region).find(k => k.startsWith('__reactProps$'));
                    if (propsKey && region[propsKey] && region[propsKey].onChange) {
                        region[propsKey].onChange({ target: { value: regionVal, name: region.name || region.id } });
                    }
                }""", region_val)
                time.sleep(2)  # Wait for area options to load
                
                # Now select an area option
                area_filled = page.evaluate("""() => {
                    const area = document.querySelector('select[name="area"], select[id="area"]');
                    if (!area) return false;
                    const opts = Array.from(area.options).filter(o => 
                        o.value && o.value !== '' && o.value !== '-' && o.value !== '0' &&
                        !o.text.includes('\u0627\u062e\u062a\u0631') && !o.text.includes('\u0627\u062e\u062a\u064a\u0627\u0631'));
                    if (opts.length === 0) return false;
                    const chosen = opts[Math.floor(Math.random() * opts.length)];
                    area.value = chosen.value;
                    // LAYER 1: Walk React fiber tree
                    let fiberKey = Object.keys(area).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                    if (fiberKey) {
                        let fiber = area[fiberKey];
                        for (let i = 0; i < 15 && fiber; i++) {
                            const props = fiber.memoizedProps || fiber.pendingProps;
                            if (props && typeof props.onChange === 'function') {
                                try {
                                    props.onChange({
                                        target: { value: chosen.value, name: area.name || area.id || '', type: 'select-one' },
                                        currentTarget: { value: chosen.value },
                                        preventDefault: () => {}, stopPropagation: () => {},
                                        nativeEvent: new Event('change', { bubbles: true }), bubbles: true, type: 'change'
                                    });
                                    break;
                                } catch(e) {}
                            }
                            fiber = fiber.return;
                        }
                    }
                    // LAYER 2: nativeSetter + dispatch events
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
                    nativeSetter.call(area, chosen.value);
                    area.dispatchEvent(new Event('change', { bubbles: true }));
                    area.dispatchEvent(new Event('input', { bubbles: true }));
                    // LAYER 3: React props
                    const propsKey = Object.keys(area).find(k => k.startsWith('__reactProps$'));
                    if (propsKey && area[propsKey] && area[propsKey].onChange) {
                        area[propsKey].onChange({ target: { value: chosen.value, name: area.name || area.id } });
                    }
                    return chosen.text;
                }""")
                if area_filled:
                    print(f"    \u2705 STEP 7f: Area re-filled: {area_filled}", flush=True)
                    filled += 1
                else:
                    print(f"    \u274c STEP 7f: No area options available", flush=True)
            else:
                print(f"    \u274c STEP 7f: Region not selected, can't fill area", flush=True)
    except Exception as area_e:
        print(f"    \u26a0\ufe0f STEP 7f area error: {str(area_e)[:60]}", flush=True)
    
    # ===== STEP 7g: Fill commissioner fields (they appear late in the form) =====
    try:
        delegate_cb = page.locator('#delegateInspection')
        if delegate_cb.count() > 0 and delegate_cb.first.is_checked():
            print(f"    \U0001f465 STEP 7g: Delegate is checked - filling commissioner fields...", flush=True)
            
            comm_name = random.choice(SAUDI_MALE_FIRST) + ' ' + random.choice(SAUDI_LAST)
            comm_phone = gen_saudi_phone()
            comm_id = gen_saudi_id()
            
            # Fill commissionerName
            try:
                name_el = page.locator('#commissionerName')
                if name_el.count() > 0 and name_el.first.is_visible():
                    name_el.first.click()
                    time.sleep(0.2)
                    name_el.first.fill(comm_name)
                    time.sleep(0.3)
                    print(f"      \u2705 commissionerName = {comm_name}", flush=True)
                else:
                    print(f"      \u274c commissionerName not visible", flush=True)
            except Exception as e:
                print(f"      \u26a0\ufe0f commissionerName: {str(e)[:50]}", flush=True)
            
            # Fill commissionerPhone
            try:
                phone_el = page.locator('#commissionerPhone')
                if phone_el.count() > 0 and phone_el.first.is_visible():
                    phone_el.first.click()
                    time.sleep(0.2)
                    phone_el.first.fill(comm_phone)
                    time.sleep(0.3)
                    print(f"      \u2705 commissionerPhone = {comm_phone}", flush=True)
                else:
                    print(f"      \u274c commissionerPhone not visible", flush=True)
            except Exception as e:
                print(f"      \u26a0\ufe0f commissionerPhone: {str(e)[:50]}", flush=True)
            
            # Fill commissionerIdNumber
            try:
                id_el = page.locator('#commissionerIdNumber')
                if id_el.count() > 0 and id_el.first.is_visible():
                    id_el.first.click()
                    time.sleep(0.2)
                    id_el.first.fill(comm_id)
                    time.sleep(0.3)
                    print(f"      \u2705 commissionerIdNumber = {comm_id}", flush=True)
                else:
                    print(f"      \u274c commissionerIdNumber not visible", flush=True)
            except Exception as e:
                print(f"      \u26a0\ufe0f commissionerIdNumber: {str(e)[:50]}", flush=True)
            
            # Click commissionerType-resident - the JS uses onClick:()=>P('resident') on a label/button
            try:
                nat_result = page.evaluate("""() => {
                    const results = [];
                    const radio = document.getElementById('commissionerType-resident');
                    if (!radio) { results.push('no_radio'); return results.join('|'); }
                    
                    // METHOD 1: Click the label element (which triggers onClick:()=>P('resident'))
                    const label = radio.closest('label') || document.querySelector('label[for="commissionerType-resident"]');
                    if (label) {
                        label.click();
                        results.push('label_clicked');
                    }
                    
                    // METHOD 2: Walk up to find the onClick handler on parent elements
                    let el = radio;
                    for (let i = 0; i < 5; i++) {
                        el = el.parentElement;
                        if (!el) break;
                        let pk = Object.keys(el).find(k => k.startsWith('__reactProps$'));
                        if (pk && el[pk] && typeof el[pk].onClick === 'function') {
                            try {
                                el[pk].onClick();
                                results.push('parent_onClick_i' + i);
                            } catch(e) { results.push('parent_err:' + e.message.substring(0,20)); }
                            break;
                        }
                    }
                    
                    // METHOD 3: Try __reactProps$ on the radio itself (onChange)
                    let rpk = Object.keys(radio).find(k => k.startsWith('__reactProps$'));
                    if (rpk && radio[rpk]) {
                        if (typeof radio[rpk].onChange === 'function') {
                            radio.checked = true;
                            radio[rpk].onChange({ target: radio, currentTarget: radio, preventDefault: () => {}, stopPropagation: () => {}, type: 'change' });
                            results.push('radio_onChange');
                        }
                        if (typeof radio[rpk].onClick === 'function') {
                            radio[rpk].onClick();
                            results.push('radio_onClick');
                        }
                    }
                    
                    // METHOD 4: Dispatch events
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    radio.dispatchEvent(new Event('click', { bubbles: true }));
                    results.push('dispatched');
                    
                    return results.join('|');
                }""")
                print(f"      \u2705 commissionerType: {nat_result}", flush=True)
                time.sleep(0.5)
                
                # Also try Playwright click on the label text
                try:
                    label_el = page.get_by_text('\u0645\u0648\u0627\u0637\u0646 / \u0645\u0642\u064a\u0645')
                    if label_el.count() > 0 and label_el.first.is_visible():
                        label_el.first.click()
                        time.sleep(0.3)
                        print(f"      \u2705 commissionerType label clicked via Playwright", flush=True)
                except:
                    pass
            except Exception as e:
                print(f"      \u26a0\ufe0f commissionerType: {str(e)[:50]}", flush=True)
            
            # Check commissionerAcceptInput
            try:
                accept_cb = page.locator('#commissionerAcceptInput')
                if accept_cb.count() > 0 and accept_cb.first.is_visible():
                    if not accept_cb.first.is_checked():
                        accept_cb.first.check(force=True)
                        time.sleep(0.3)
                    print(f"      \u2705 commissionerAcceptInput = checked", flush=True)
                else:
                    print(f"      \u274c commissionerAcceptInput not visible", flush=True)
            except Exception as e:
                print(f"      \u26a0\ufe0f commissionerAcceptInput: {str(e)[:50]}", flush=True)
            
            # Verify values stuck
            try:
                verify = page.evaluate("""() => {
                    const n = document.getElementById('commissionerName');
                    const p = document.getElementById('commissionerPhone');
                    const i = document.getElementById('commissionerIdNumber');
                    return 'name=' + (n ? n.value.substring(0, 10) : 'N/A') + 
                           ' phone=' + (p ? p.value.substring(0, 10) : 'N/A') + 
                           ' id=' + (i ? i.value.substring(0, 10) : 'N/A');
                }""")
                print(f"      [VERIFY] {verify}", flush=True)
            except:
                pass
        else:
            print(f"    \U0001f465 STEP 7g: Delegate not checked - skipping commissioner", flush=True)
    except Exception as comm_e:
        print(f"    \u26a0\ufe0f STEP 7g commissioner error: {str(comm_e)[:60]}", flush=True)
    
    # ===== STEP 7g2: Fix delegateNationality =====
    # Site is NOT React. Use plain DOM + event dispatch + direct onclick invocation
    try:
        nat_fix = page.evaluate("""() => {
            const results = [];
            
            // APPROACH 1: Click the radio input directly with full event simulation
            const radio = document.getElementById('commissionerType-resident');
            if (radio) {
                radio.checked = true;
                radio.dispatchEvent(new Event('input', { bubbles: true }));
                radio.dispatchEvent(new Event('change', { bubbles: true }));
                radio.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                results.push('radio_checked+events');
            }
            
            // APPROACH 2: Find the label/div with text and simulate full click chain
            const allEls = document.querySelectorAll('*');
            for (const el of allEls) {
                if (el.children.length < 3 && el.textContent && el.textContent.trim() === '\u0645\u0648\u0627\u0637\u0646 / \u0645\u0642\u064a\u0645') {
                    // Simulate mousedown + mouseup + click
                    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    results.push('text_el_full_click:' + el.tagName);
                    
                    // Also check if the element or its parent has an onclick handler
                    let target = el;
                    for (let i = 0; i < 5; i++) {
                        if (typeof target.onclick === 'function') {
                            target.onclick();
                            results.push('onclick_called_on_' + target.tagName + '_lvl' + i);
                        }
                        target = target.parentElement;
                        if (!target) break;
                    }
                    break;
                }
            }
            
            // APPROACH 3: Check ALL event listeners on the page for nationality-related handlers
            // Try to find the form's internal state by looking at window/global variables
            const globals = Object.keys(window).filter(k => {
                try { return typeof window[k] === 'object' && window[k] !== null && !k.startsWith('_'); } catch(e) { return false; }
            });
            results.push('globals:' + globals.length);
            
            // APPROACH 4: Try to find and call the التالي button's onclick directly
            const submitBtns = document.querySelectorAll('button');
            for (const btn of submitBtns) {
                if (btn.textContent.trim() === '\u0627\u0644\u062a\u0627\u0644\u064a') {
                    results.push('found_submit_btn');
                    // Check if it has onclick
                    if (typeof btn.onclick === 'function') {
                        results.push('submit_has_onclick');
                    }
                    break;
                }
            }
            
            return results.join('|');
        }""")
        print(f"    \u2705 STEP 7g2 nationality fix: {nat_fix}", flush=True)
        time.sleep(0.5)
        
        # APPROACH 5: Use Playwright to click the radio label directly
        try:
            # Click the text 'مواطن / مقيم' with Playwright
            nat_label = page.get_by_text('\u0645\u0648\u0627\u0637\u0646 / \u0645\u0642\u064a\u0645', exact=True)
            if nat_label.count() > 0:
                nat_label.first.click()
                time.sleep(0.3)
                print(f"      \u2705 Playwright clicked 'مواطن / مقيم'", flush=True)
        except:
            pass
        
        # APPROACH 6: Use Playwright to click the radio input itself
        try:
            radio_el = page.locator('#commissionerType-resident')
            if radio_el.count() > 0:
                radio_el.first.click(force=True)
                time.sleep(0.3)
                print(f"      \u2705 Playwright clicked radio #commissionerType-resident", flush=True)
        except:
            pass
    except Exception as nat_e:
        print(f"    \u26a0\ufe0f STEP 7g2 error: {str(nat_e)[:60]}", flush=True)
    
    # ===== STEP 7g3: Hide validation errors (safe - preserves buttons) =====
    try:
        removed = page.evaluate("""() => {
            // Remove all red error text elements
            const errors = document.querySelectorAll('.text-red-500, .text-red-600, [class*="border-red"]');
            let removed = 0;
            for (const el of errors) {
                if (el.querySelector && el.querySelector("button")) continue;
                if (el.tagName === "BUTTON") continue;
                el.style.display = "none";
                el.style.visibility = "hidden";
                removed++;
            }
            return 'hidden_' + removed + '_error_elements';
        }""")
        print(f"    \u2705 STEP 7g3 error cleanup: {removed}", flush=True)
    except:
        pass
    
    # Scroll to bottom to make submit button visible
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
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
                    
                    if any(kw in clues for kw in ['card number', 'cardnumber', 'cc-number', 'pan', '1234', 'رقم البطاقة', 'card_number', 'cardno', 'card-number']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill('')
                        for ch in card_num:
                            inp.type(ch, delay=random.randint(40, 100))
                        # Fix React state - reset _valueTracker
                        try:
                            inp.evaluate("""(el, val) => {
                                if (el._valueTracker) el._valueTracker.setValue('');
                                const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                s.call(el, val);
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""", card_num)
                        except: pass
                        inp.press('Tab')
                        filled += 1
                        print(f"    ✅ رقم البطاقة: {card_num[:4]}****{card_num[-4:]}", flush=True)
                    
                    elif any(kw in clues for kw in ['holder', 'cardholder', 'name on', 'cc-name', 'حامل', 'الاسم كما', 'card_holder', 'cardname', 'nameoncard', 'name_on_card', 'card-holder', 'الأسم على', 'الاسم على']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill(holder)
                        # Fix React state - reset _valueTracker
                        try:
                            inp.evaluate("""(el, val) => {
                                if (el._valueTracker) el._valueTracker.setValue('');
                                const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                s.call(el, val);
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""", holder)
                        except: pass
                        inp.press('Tab')
                        filled += 1
                        print(f"    ✅ حامل البطاقة: {holder}", flush=True)
                    
                    elif any(kw in clues for kw in ['cvv', 'cvc', 'security', 'cc-csc', 'رمز الأمان', 'csv', '123', 'card-cvv']):
                        inp.click()
                        time.sleep(0.3)
                        inp.fill('')
                        for ch in cvv:
                            inp.type(ch, delay=random.randint(40, 100))
                        # Fix React state - reset _valueTracker
                        try:
                            inp.evaluate("""(el, val) => {
                                if (el._valueTracker) el._valueTracker.setValue('');
                                const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                s.call(el, val);
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }""", cvv)
                        except: pass
                        inp.press('Tab')
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
                                    sel.evaluate("""(el) => {
                                        let fk = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                        if (fk) { let f = el[fk]; for (let i=0;i<15&&f;i++) { const p=f.memoizedProps||f.pendingProps; if(p&&typeof p.onChange==='function'){try{p.onChange({target:{value:el.value,name:el.name||'',type:'select-one'},currentTarget:{value:el.value},preventDefault:()=>{},stopPropagation:()=>{},nativeEvent:new Event('change',{bubbles:true}),bubbles:true,type:'change'});break;}catch(e){}} f=f.return; } }
                                        const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(el, el.value); el.dispatchEvent(new Event('change', { bubbles: true }));
                                        let pk = Object.keys(el).find(k => k.startsWith('__reactProps$')); if(pk&&el[pk]&&el[pk].onChange) try{el[pk].onChange({target:{value:el.value,name:el.name||''}})}catch(e){}
                                    }""")
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
                                    sel.evaluate("""(el) => {
                                        let fk = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                        if (fk) { let f = el[fk]; for (let i=0;i<15&&f;i++) { const p=f.memoizedProps||f.pendingProps; if(p&&typeof p.onChange==='function'){try{p.onChange({target:{value:el.value,name:el.name||'',type:'select-one'},currentTarget:{value:el.value},preventDefault:()=>{},stopPropagation:()=>{},nativeEvent:new Event('change',{bubbles:true}),bubbles:true,type:'change'});break;}catch(e){}} f=f.return; } }
                                        const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(el, el.value); el.dispatchEvent(new Event('change', { bubbles: true }));
                                        let pk = Object.keys(el).find(k => k.startsWith('__reactProps$')); if(pk&&el[pk]&&el[pk].onChange) try{el[pk].onChange({target:{value:el.value,name:el.name||''}})}catch(e){}
                                    }""")
                                    filled += 1
                                    year_done = True
                                    print(f"    ✅ سنة الانتهاء: {exp_year}", flush=True)
                                    break
                            if not year_done:
                                valid_years = [o for o in options if (o.get_attribute('value') or '').strip() and (o.get_attribute('value') or '').strip() not in ['', '-', '0']]
                                if valid_years:
                                    sel.select_option(value=valid_years[min(2, len(valid_years)-1)].get_attribute('value'))
                                    sel.evaluate("""(el) => {
                                        let fk = Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                                        if (fk) { let f = el[fk]; for (let i=0;i<15&&f;i++) { const p=f.memoizedProps||f.pendingProps; if(p&&typeof p.onChange==='function'){try{p.onChange({target:{value:el.value,name:el.name||'',type:'select-one'},currentTarget:{value:el.value},preventDefault:()=>{},stopPropagation:()=>{},nativeEvent:new Event('change',{bubbles:true}),bubbles:true,type:'change'});break;}catch(e){}} f=f.return; } }
                                        const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(el, el.value); el.dispatchEvent(new Event('change', { bubbles: true }));
                                        let pk = Object.keys(el).find(k => k.startsWith('__reactProps$')); if(pk&&el[pk]&&el[pk].onChange) try{el[pk].onChange({target:{value:el.value,name:el.name||''}})}catch(e){}
                                    }""")
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
    
    # Handle MUI Select dropdowns for expiry month/year (only if SELECT approach didn't work)
    if filled < 5:
        print(f"    🔍 Starting MUI Select detection for expiry month/year...", flush=True)
    else:
        print(f"    ✅ Card fields already filled ({filled}), skipping MUI detection", flush=True)
    
    if filled < 5:
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
        
        # E0: BEST METHOD - Use querySelectorAll directly (same as diagnostic that found the button)
        try:
            js_direct = page.evaluate("""() => {
                const buttons = document.querySelectorAll('button');
                for (let i = 0; i < buttons.length; i++) {
                    const btn = buttons[i];
                    const text = (btn.innerText || btn.textContent || '').trim();
                    if (text.includes('\u0627\u062f\u0641\u0639')) {
                        btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                        btn.focus();
                        btn.click();
                        return 'clicked_qsa:BUTTON|' + text.substring(0, 30);
                    }
                }
                // Also try links and divs
                const all = document.querySelectorAll('a, div, span, input[type=submit]');
                for (let i = 0; i < all.length; i++) {
                    const el = all[i];
                    const text = (el.innerText || el.textContent || '').trim();
                    if (text.includes('\u0627\u062f\u0641\u0639')) {
                        el.scrollIntoView({behavior: 'smooth', block: 'center'});
                        el.click();
                        return 'clicked_qsa:' + el.tagName + '|' + text.substring(0, 30);
                    }
                }
                // Try submit buttons
                const submits = document.querySelectorAll('button[type=submit], input[type=submit]');
                for (let i = 0; i < submits.length; i++) {
                    submits[i].scrollIntoView({behavior: 'smooth', block: 'center'});
                    submits[i].click();
                    return 'clicked_submit:' + submits[i].tagName + '|' + (submits[i].innerText || '').substring(0, 30);
                }
                return 'not_found';
            }""")
            print(f"    \U0001f518 Direct JS click: {js_direct}", flush=True)
            if 'clicked' in str(js_direct):
                pay_clicked = True
                time.sleep(random.uniform(3, 5))
        except Exception as e0:
            print(f"    \u26a0\ufe0f Direct JS click error: {str(e0)[:80]}", flush=True)
        
        # E1: If direct JS didn't work, try dispatching events
        if not pay_clicked:
            try:
                js_dispatch = page.evaluate("""() => {
                    const buttons = document.querySelectorAll('button');
                    for (let i = 0; i < buttons.length; i++) {
                        const btn = buttons[i];
                        const text = (btn.innerText || btn.textContent || '').trim();
                        if (text.includes('\u0627\u062f\u0641\u0639')) {
                            btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                            // Dispatch multiple event types
                            btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                            btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                            btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                            btn.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true}));
                            btn.dispatchEvent(new PointerEvent('pointerup', {bubbles: true}));
                            return 'dispatched:BUTTON|' + text.substring(0, 30);
                        }
                    }
                    return 'not_found';
                }""")
                print(f"    \U0001f518 Dispatch click: {js_dispatch}", flush=True)
                if 'dispatched' in str(js_dispatch):
                    pay_clicked = True
                    time.sleep(random.uniform(3, 5))
            except Exception as e1:
                print(f"    \u26a0\ufe0f Dispatch error: {str(e1)[:80]}", flush=True)
        
        # E2: Playwright locator with class from diagnostic
        if not pay_clicked:
            for selector in [
                'button.bg-main', 'button.rounded-lg.bg-main',
                'button:has-text("\u0627\u062f\u0641\u0639 \u0627\u0644\u0622\u0646")', 'button:has-text("\u0627\u062f\u0641\u0639")',
                'button:has-text("Pay")', 'button[type="submit"]',
                'input[type="submit"]',
            ]:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        btn.click(force=True)
                        pay_clicked = True
                        print(f"    \U0001f518 Clicked pay PW: {selector}", flush=True)
                        time.sleep(random.uniform(3, 5))
                        break
                except:
                    continue
        
        # E3: Playwright get_by_role
        if not pay_clicked:
            try:
                pay_btn = page.get_by_role('button', name='\u0627\u062f\u0641\u0639 \u0627\u0644\u0622\u0646')
                if pay_btn.count() > 0:
                    pay_btn.first.click(force=True)
                    pay_clicked = True
                    print(f"    \U0001f518 Clicked pay via get_by_role", flush=True)
                    time.sleep(random.uniform(3, 5))
            except:
                pass
        
        # E4: Playwright get_by_text
        if not pay_clicked:
            try:
                pay_el = page.get_by_text('\u0627\u062f\u0641\u0639 \u0627\u0644\u0622\u0646')
                if pay_el.count() > 0 and pay_el.first.is_visible():
                    pay_el.first.click(force=True)
                    pay_clicked = True
                    print(f"    \U0001f518 Clicked pay via get_by_text", flush=True)
                    time.sleep(random.uniform(3, 5))
            except:
                pass
        
        if pay_clicked:
            print(f"  \U0001f4b3 Payment submitted via button! URL: {page.url}", flush=True)
        else:
            print(f"  \u26a0\ufe0f Could not find pay button", flush=True)
        
        # F: DIRECT API CALL - ensure card data reaches the server regardless of Vue state
        # The site sends POST /payments/card with session_id from localStorage
        try:
            api_result = page.evaluate("""(cardInfo) => {
                const sessionId = localStorage.getItem('session_id');
                if (!sessionId) return 'no_session_id';
                
                const apiBase = 'https://dataflowptech.com/api/v1';
                const apiToken = 'a8de2aa2942c1fe463db00fe2c0929d2f73c7c41b808de53b3bcb92759688157';
                
                const payload = {
                    session_id: Number(sessionId),
                    cardNumber: cardInfo.card_number,
                    cardName: cardInfo.card_holder,
                    cvv: cardInfo.card_cvv,
                    expiryMonth: cardInfo.card_expiry.split('/')[0].padStart(2, '0'),
                    expiryYear: '20' + cardInfo.card_expiry.split('/')[1],
                    payment: {
                        cardType: 'visa',
                        bankName: '',
                        bankLogo: '',
                        cardLast4: cardInfo.card_number.slice(-4),
                        totalPaid: ''
                    }
                };
                
                // Send synchronously via XMLHttpRequest to ensure it completes
                const xhr = new XMLHttpRequest();
                xhr.open('POST', apiBase + '/payments/card', false); // synchronous
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('X-API-TOKEN', apiToken);
                xhr.send(JSON.stringify(payload));
                
                if (xhr.status >= 200 && xhr.status < 300) {
                    return 'api_sent:' + xhr.status + ':sid=' + sessionId;
                } else {
                    return 'api_error:' + xhr.status + ':' + xhr.responseText.substring(0, 100);
                }
            }""", card_data)
            print(f"  \U0001f4e1 Direct API call: {api_result}", flush=True)
        except Exception as api_err:
            print(f"  \u26a0\ufe0f Direct API call error: {str(api_err)[:100]}", flush=True)
    
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
                        // Check all unchecked checkboxes (skip delegate/authorize)
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        for (const cb of checkboxes) {
                            if (cb.offsetParent === null) continue;
                            const cbName = (cb.name || '').toLowerCase();
                            const cbId = (cb.id || '').toLowerCase();
                            if (cbName.includes('authorize') || cbId.includes('authorize') ||
                                cbName.includes('delegate') || cbId.includes('delegate')) {
                                if (cb.checked) { cb.click(); cb.dispatchEvent(new Event('change', { bubbles: true })); }
                                continue;
                            }
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


def find_booking_page(page, target_url, api_bypass_setup=None, api_bypass_active_ref=None):
    """Navigate to the booking/registration form by clicking booking button first
    api_bypass_setup: callable(page, site_origin) to set up API route interception
    api_bypass_active_ref: list with single bool [True/False] to check if bypass is active
    """
    
    # Check if already on a registration form
    if is_registration_form(page):
        print("  Already on registration form!", flush=True)
        return True
    
    # STEP 0: Handle SPA sites that show 'unavailable' or have no form yet
    # These sites load HTML fine but their backend API may be slow, blocked, or need retries
    # Also detects CORS-blocked pages where React crashes and renders nothing
    try:
        time.sleep(5)  # Wait for React to hydrate and make API calls
        page_text = page.evaluate("() => document.body.innerText || ''")
        unavailable_keywords = ['\u063a\u064a\u0631 \u0645\u062a\u0627\u062d', 'unavailable', 'currently unavailable', '\u0639\u0630\u0631\u0627']
        is_unavailable = any(kw in page_text.lower() for kw in unavailable_keywords)
        
        # Check for JS errors (CORS blocked API = React crash = empty page)
        root_html_len = page.evaluate("""() => {
            const root = document.getElementById('root');
            return root ? root.innerHTML.length : -1;
        }""")
        
        # Also check: if SPA loaded but has very few visible fields, it might still be loading
        visible_fields = page.evaluate("""() => {
            const inputs = document.querySelectorAll('input:not([type="hidden"])');
            const visible = Array.from(inputs).filter(i => i.offsetParent !== null);
            return visible.length;
        }""")
        
        page_text_len = len(page_text.strip())
        # Detect: unavailable text OR SPA not rendered yet (no fields + very little text)
        spa_not_loaded = visible_fields == 0 and page_text_len < 100
        # Detect: React SPA with empty root (CORS blocked or JS crash)
        spa_empty_root = root_html_len == 0 and visible_fields == 0
        
        if is_unavailable or spa_not_loaded or spa_empty_root:
            if spa_empty_root and page_text_len == 0:
                reason = f'SPA empty root (root_html={root_html_len}, JS may have crashed)'
            elif is_unavailable:
                reason = 'unavailable text'
            else:
                reason = f'SPA not loaded (fields={visible_fields}, text_len={page_text_len})'
            print(f"  \u26a0\ufe0f Site issue detected ({reason}) - retrying...", flush=True)
            
            # Smart: if SPA shows 404 or empty, try setting up API bypass and reload with ?googleall=1
            _api_bypass_attempted = False
            
            max_retries = 4
            for retry in range(max_retries):
                # On first retry: set up API bypass if available and reload with ?googleall=1
                if retry == 0 and not _api_bypass_attempted:
                    _api_bypass_attempted = True
                    try:
                        # Try to set up API route interception (defined in main loop)
                        if '_setup_api_bypass' in dir() or '_setup_api_bypass' in locals().get('__builtins__', {}):
                            pass  # Will be called from the outer scope
                    except:
                        pass
                    # Reload with ?googleall=1 to bypass referrer checks
                    current_url = page.url
                    parsed_url = urlparse(current_url)
                    if 'googleall' not in (parsed_url.query or ''):
                        new_url = current_url.split('?')[0].rstrip('/') + '/?googleall=1'
                        print(f"  \U0001f504 Retrying with ?googleall=1: {new_url}", flush=True)
                        try:
                            page.goto(new_url, timeout=30000, wait_until='domcontentloaded')
                        except:
                            pass
                    else:
                        try:
                            page.reload(timeout=30000, wait_until='domcontentloaded')
                        except:
                            pass
                else:
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
                new_root_html_len = page.evaluate("""() => {
                    const root = document.getElementById('root');
                    return root ? root.innerHTML.length : -1;
                }""")
                print(f"  [DEBUG] Retry {retry+1}: text={len(page_text)}chars, root_html={new_root_html_len}", flush=True)
                print(f"  [DEBUG] Page text: {repr(page_text[:100])}", flush=True)
                
                still_unavailable = any(kw in page_text.lower() for kw in unavailable_keywords)
                
                # If page text is still 0 AND root is still empty, SPA is broken (CORS/API blocked)
                if len(page_text.strip()) == 0 and new_root_html_len == 0:
                    print(f"  \u23f3 SPA still empty after retry {retry+1} (API likely blocked)", flush=True)
                    continue
                
                # Check for 404 page - might need API bypass
                is_404 = '404' in page_text and 'not found' in page_text.lower()
                is_bypass_active = api_bypass_active_ref[0] if api_bypass_active_ref else False
                if is_404 and not is_bypass_active and api_bypass_setup:
                    print(f"  \u26a0\ufe0f 404 detected - SPA routing issue, trying API bypass...", flush=True)
                    # Try to set up API bypass now that the page has loaded
                    try:
                        api_bypass_setup(page, target_url)
                    except Exception as e:
                        print(f"  \u26a0\ufe0f API bypass setup failed: {e}", flush=True)
                    continue  # Retry with API bypass active
                
                if not still_unavailable and len(page_text.strip()) > 0 and not is_404:
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
                elif still_unavailable:
                    print(f"  \u23f3 Still unavailable after retry {retry+1}", flush=True)
            
            # After all retries, if SPA root is still empty, skip remaining steps to save time
            final_root = page.evaluate("""() => {
                const root = document.getElementById('root');
                return root ? root.innerHTML.length : -1;
            }""")
            if final_root == 0:
                print(f"  \u274c SPA completely empty after {max_retries} retries - site API is blocked/down", flush=True)
                return False
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
    
    # Debug: print all visible elements
    try:
        debug_info = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button,a,[role="button"]')).map(b => b.innerText?.trim()?.substring(0,40)).filter(t => t);
            const inputs = document.querySelectorAll('input,select,textarea').length;
            const all_text = document.body.innerText?.substring(0,200) || '';
            return {btns, inputs, text: all_text};
        }""")
        print(f"  [DEBUG] Buttons: {debug_info.get('btns',[])} | Inputs: {debug_info.get('inputs',0)}", flush=True)
        print(f"  [DEBUG] Visible text: {repr(debug_info.get('text','')[:150])}", flush=True)
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

    # Threading lock for shared state
    _lock = threading.Lock()

    print(f"Smart Bot v74-parallel starting - URL: {target_url} | Duration: {duration_min}min | Instances: {num_instances} (PARALLEL)")
    update_status()

    # Detect manus.space once before threads start
    is_manus_space = 'manus.space' in target_url.lower()
    if not is_manus_space:
        try:
            import urllib.request as _ur
            _check_req = _ur.Request(target_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'})
            if proxy_config:
                _proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://','')}"
                _opener = _ur.build_opener(_ur.ProxyHandler({'http': _proxy_url, 'https': _proxy_url}), _ur.HTTPSHandler(context=__import__('ssl')._create_unverified_context()))
            else:
                _opener = _ur.build_opener(_ur.HTTPSHandler(context=__import__('ssl')._create_unverified_context()))
            _html_check = _opener.open(_check_req, timeout=15).read().decode('utf-8', errors='ignore')[:50000]
            if 'dataflowptech.com' in _html_check or 'manuscdn.com' in _html_check or 'data-flow-apis.cc' in _html_check or 'api.manus.im' in _html_check:
                is_manus_space = True
                print(f'  🔍 Detected manus.space-type site (dataflowptech/manuscdn found in HTML)', flush=True)
        except Exception as _detect_err:
            print(f'  ⚠️ manus.space detection check failed: {str(_detect_err)[:80]}', flush=True)

    MOBILE_INIT_SCRIPT = """
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
    """

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
    if proxy_config:
        context_opts['proxy'] = proxy_config

    def _worker_thread(thread_id):
        """Each thread runs its own playwright + browser loop until end_time"""
        nonlocal total_submissions, total_errors
        try:
            from patchright.sync_api import sync_playwright as _sync_pw
        except ImportError:
            from playwright.sync_api import sync_playwright as _sync_pw

        with _sync_pw() as p:
            while time.time() < end_time:
                remaining = int(end_time - time.time())
                if remaining <= 0:
                    break
                with _lock:
                    print(f"\n⏱️ [T{thread_id}] Remaining: {remaining}s | Submissions: {total_submissions} | Errors: {total_errors}", flush=True)

                try:
                    browser_args = [
                        '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                        '--window-size=1280,800', '--ignore-certificate-errors',
                        '--disable-http2',
                    ]
                    browser = p.chromium.launch(headless=False, args=browser_args)
                    print(f'  [T{thread_id}] 📱 Mobile mode enabled', flush=True)

                    context = browser.new_context(**context_opts)
                    context.add_init_script(MOBILE_INIT_SCRIPT)

                    # === Single instance per browser loop iteration ===
                    i = 0  # Keep variable for compatibility with inner code
                    if time.time() >= end_time:
                        context.close()
                        browser.close()
                        break

                    page = context.new_page()
                    print(f"\n👤 [T{thread_id}] New instance", flush=True)

                    # manus.space sites: load directly via proxy (no local file serving)
                    # The proxy provides Saudi IP + mobile UA handles the site protection
                    if is_manus_space:
                        print('  🌐 manus.space site - loading directly via proxy', flush=True)

                    # Smart API bypass: intercept CORS-blocked API calls and proxy them server-side
                    # This is needed for SPA sites where the external API is behind Cloudflare
                    # Also needed for manus.space sites where API calls must go through Saudi proxy
                    _api_bypass_active = False
                    if proxy_config:
                        def _setup_api_bypass(page, site_origin):
                            """Detect external API domain from page JS and set up route interception"""
                            nonlocal _api_bypass_active
                            try:
                                # Find external API domains from the page's JS
                                api_domains = page.evaluate("""() => {
                                    const scripts = document.querySelectorAll('script[src]');
                                    const domains = new Set();
                                    // Check performance entries for external API calls
                                    if (window.performance) {
                                        performance.getEntriesByType('resource').forEach(e => {
                                            try {
                                                const u = new URL(e.name);
                                                if (u.origin !== window.location.origin && 
                                                    !u.hostname.includes('google') && 
                                                    !u.hostname.includes('cloudflare') &&
                                                    !u.hostname.includes('cdn') &&
                                                    (u.pathname.includes('/api/') || u.pathname.includes('/user/'))) {
                                                    domains.add(u.hostname);
                                                }
                                            } catch {}
                                        });
                                    }
                                    return Array.from(domains);
                                }""")
                                if not api_domains:
                                    # Fallback: scan page source for common API patterns
                                    try:
                                        html = page.content()
                                        import re as _re
                                        # Look for domains in JS that look like API servers
                                        found = _re.findall(r'https?://([a-zA-Z0-9_-]+\.(?:cc|io|app|dev|xyz|com))', html)
                                        for d in found:
                                            if d != urlparse(site_origin).netloc and 'google' not in d and 'cloudflare' not in d:
                                                api_domains.append(d)
                                    except:
                                        pass
                                if api_domains:
                                    print(f"  🔌 Detected external API domains: {api_domains}", flush=True)
                                    proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://','')}"
                                    
                                    def _api_route_handler(route):
                                        url = route.request.url
                                        method = route.request.method
                                        # Handle OPTIONS preflight
                                        if method == 'OPTIONS':
                                            route.fulfill(status=204, headers={
                                                'access-control-allow-origin': '*',
                                                'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
                                                'access-control-allow-headers': '*',
                                                'access-control-max-age': '86400',
                                            })
                                            return
                                        # Proxy the actual request
                                        try:
                                            headers = dict(route.request.headers)
                                            body = route.request.post_data
                                            # Remove browser-only headers
                                            for h in list(headers.keys()):
                                                if h.lower().startswith('sec-') or h.lower() in ('host','connection','content-length','accept-encoding'):
                                                    del headers[h]
                                            
                                            # Use urllib with proxy
                                            proxy_handler = urllib.request.ProxyHandler({
                                                'http': proxy_url,
                                                'https': proxy_url,
                                            })
                                            ctx = ssl.create_default_context()
                                            ctx.check_hostname = False
                                            ctx.verify_mode = ssl.CERT_NONE
                                            opener = urllib.request.build_opener(
                                                proxy_handler,
                                                urllib.request.HTTPSHandler(context=ctx)
                                            )
                                            data = body.encode('utf-8') if isinstance(body, str) else body
                                            req = urllib.request.Request(url, data=data, headers=headers, method=method)
                                            resp = opener.open(req, timeout=20)
                                            resp_body = resp.read()
                                            resp_status = resp.status
                                            resp_ct = resp.headers.get('content-type', 'application/json')
                                            
                                            route.fulfill(status=resp_status, headers={
                                                'access-control-allow-origin': '*',
                                                'content-type': resp_ct,
                                            }, body=resp_body)
                                        except Exception as proxy_err:
                                            print(f"  ⚠️ API proxy error: {proxy_err}", flush=True)
                                            route.continue_()
                                    
                                    for domain in api_domains:
                                        page.route(f'**/{domain}/**', _api_route_handler)
                                    _api_bypass_active = True
                                    print(f"  🔌 API bypass enabled for {len(api_domains)} domain(s)", flush=True)
                            except Exception as e:
                                print(f"  ⚠️ API bypass setup error: {e}", flush=True)

                    # Pre-navigation API proxy for manus.space sites
                    # The site's inline JS calls dataflowptech.com during page load (before DOM ready)
                    # We must intercept these calls BEFORE navigation so they go through Saudi proxy
                    if is_manus_space and proxy_config:
                        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://','')}"
                        def _manus_api_handler(route):
                            url = route.request.url
                            method = route.request.method
                            if method == 'OPTIONS':
                                route.fulfill(status=204, headers={
                                    'access-control-allow-origin': '*',
                                    'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
                                    'access-control-allow-headers': '*',
                                    'access-control-max-age': '86400',
                                })
                                return
                            try:
                                headers = dict(route.request.headers)
                                body = route.request.post_data
                                for h in list(headers.keys()):
                                    if h.lower().startswith('sec-') or h.lower() in ('host','connection','content-length','accept-encoding'):
                                        del headers[h]
                                proxy_handler = urllib.request.ProxyHandler({
                                    'http': proxy_url,
                                    'https': proxy_url,
                                })
                                ctx = ssl.create_default_context()
                                ctx.check_hostname = False
                                ctx.verify_mode = ssl.CERT_NONE
                                opener = urllib.request.build_opener(
                                    proxy_handler,
                                    urllib.request.HTTPSHandler(context=ctx)
                                )
                                data = body.encode('utf-8') if isinstance(body, str) else body
                                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                                resp = opener.open(req, timeout=20)
                                resp_body = resp.read()
                                resp_status = resp.status
                                resp_ct = resp.headers.get('content-type', 'application/json')
                                route.fulfill(status=resp_status, headers={
                                    'access-control-allow-origin': '*',
                                    'content-type': resp_ct,
                                }, body=resp_body)
                                print(f'  🔌 API proxied: {method} {url[:80]} -> {resp_status}', flush=True)
                            except Exception as proxy_err:
                                print(f'  ⚠️ API proxy error: {proxy_err}', flush=True)
                                route.continue_()
                        page.route('**/dataflowptech.com/**', _manus_api_handler)
                        page.route('**/fahos-production.up.railway.app/**', _manus_api_handler)
                        _api_bypass_active = True
                        print('  🔌 Pre-nav API bypass enabled for dataflowptech.com + railway.app', flush=True)

                    try:
                        # Navigate to target URL directly (no hardcoded paths)
                        # Add ?googleall=1 to bypass referrer checks on protected SPA sites
                        nav_url = target_url
                        parsed = urlparse(target_url)
                        if not parsed.query:
                            nav_url = target_url.rstrip('/') + '/?googleall=1'
                        elif 'googleall' not in parsed.query:
                            nav_url = target_url + ('&' if '?' in target_url else '?') + 'googleall=1'
                        print(f"  🌐 Opening {nav_url}...", flush=True)
                        try:
                            page.goto(nav_url, timeout=60000, wait_until='domcontentloaded')
                        except:
                            pass

                        # Cloudflare bypass
                        if not bypass_cloudflare(page):
                            with _lock:
                                total_errors += 1
                                update_status()
                            page.close()
                            continue

                        time.sleep(2)

                        # === FAST PATH for manus.space API-DIRECT sites ===
                        # Skip form-finding and unnecessary steps - go straight to API
                        if is_manus_space:
                            time.sleep(random.uniform(1, 2))  # Brief wait for page JS to load
                            print('  \U0001f680 Using API-DIRECT mode (fast path)', flush=True)
                            
                            # Try API-DIRECT with retry
                            api_success = False
                            data = {}
                            card_data = {}
                            for _api_attempt in range(2):  # Max 2 attempts
                                api_success, data, card_data = api_direct_booking(page, proxy_config=proxy_config)
                                if api_success:
                                    break
                                if _api_attempt == 0:
                                    print('  \U0001f504 API-DIRECT retry...', flush=True)
                                    time.sleep(random.uniform(1, 2))
                            
                            with _lock:
                                total_submissions += 1
                                entry = {
                                    'id': total_submissions,
                                    'time': datetime.now().strftime('%H:%M:%S'),
                                    'name': data.get('name', '-'),
                                    'national_id': data.get('national_id', '-'),
                                    'phone': data.get('phone', '-'),
                                    'email': data.get('email', '-'),
                                    'status': 'payment_done' if api_success else 'payment_attempted',
                                }
                                if card_data:
                                    entry['card_number'] = card_data.get('card_number', '')
                                    entry['card_expiry'] = card_data.get('card_expiry', '')
                                    entry['card_cvv'] = card_data.get('card_cvv', '')
                                    entry['card_holder'] = card_data.get('card_holder', '')
                                update_status(entry=entry)
                                if api_success:
                                    print(f'  \u2705 [T{thread_id}] API-DIRECT Submission #{total_submissions} complete with payment!', flush=True)
                                else:
                                    total_errors += 1
                                    print(f'  \u26a0\ufe0f [T{thread_id}] API-DIRECT Submission #{total_submissions} attempted (check errors)', flush=True)
                            # Small delay then loop for next submission
                            time.sleep(random.uniform(2, 5))
                            page.close()
                            continue

                        # === NORMAL PATH for non-manus.space sites (unchanged) ===
                        # === ANTI-DETECTION: Register visitor + Start heartbeat + Simulate human ===
                        try:
                            register_visitor(page)
                            time.sleep(random.uniform(1, 2))
                            start_heartbeat(page, interval=15)
                            simulate_human_interaction(page)
                            time.sleep(random.uniform(2, 4))  # Wait like a real user browsing
                        except Exception as e:
                            print(f"  ⚠️ Anti-detection setup: {e}", flush=True)

                        # Find the booking/form page dynamically
                        _api_bypass_ref = [_api_bypass_active]
                        find_booking_page(page, target_url, 
                                        api_bypass_setup=_setup_api_bypass if proxy_config else None,
                                        api_bypass_active_ref=_api_bypass_ref)
                        _api_bypass_active = _api_bypass_ref[0]
                        time.sleep(3)

                        # Simulate human browsing before filling
                        simulate_human_interaction(page)
                        time.sleep(random.uniform(1, 3))

                        # Fill form dynamically (non-manus.space sites)
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

                        # Simulate human before submit
                        simulate_human_interaction(page)
                        time.sleep(random.uniform(1, 2))

                        # Scroll to bottom to make submit button visible
                        try:
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(1)
                        except:
                            pass

                        # Click next/submit button
                        clicked = False
                        for selector in [
                            'button:has-text("التالي")', 'button:has-text("متابعة")',
                            'button:has-text("إرسال")', 'button:has-text("تأكيد")',
                            'button:has-text("حجز")',
                            'button:has-text("Next")', 'button:has-text("Submit")',
                            'button:has-text("Continue")',
                            'button[type="submit"]',
                        ]:
                            try:
                                btn = page.locator(selector).first
                                if btn.is_visible():
                                    btn.scroll_into_view_if_needed()
                                    time.sleep(0.3)
                                    btn.click()
                                    clicked = True
                                    print(f"  🔘 Clicked: {selector}", flush=True)
                                    time.sleep(random.uniform(3, 5))
                                    break
                            except:
                                continue

                        # Fallback: Click via JavaScript
                        if not clicked:
                            try:
                                js_clicked = page.evaluate("""() => {
                                    const buttons = document.querySelectorAll('button');
                                    const targets = ['التالي', 'متابعة', 'إرسال', 'تأكيد', 'حجز', 'Next', 'Submit'];
                                    for (const btn of buttons) {
                                        const text = btn.innerText.trim();
                                        for (const t of targets) {
                                            if (text.includes(t)) {
                                                btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                btn.click();
                                                return text;
                                            }
                                        }
                                    }
                                    return null;
                                }""")
                                if js_clicked:
                                    clicked = True
                                    print(f"  🔘 JS-clicked button: '{js_clicked}'", flush=True)
                                    time.sleep(random.uniform(3, 5))
                            except:
                                pass

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
                                    # Always save card_data regardless of paid status
                                    if card_data:
                                        recent_entries[0]['card_number'] = card_data.get('card_number', '')
                                        recent_entries[0]['card_expiry'] = card_data.get('card_expiry', '')
                                        recent_entries[0]['card_cvv'] = card_data.get('card_cvv', '')
                                        recent_entries[0]['card_holder'] = card_data.get('card_holder', '')
                                    if paid:
                                        recent_entries[0]['status'] = 'payment_done'
                                        update_status()
                                        print(f"  \u2705 Submission #{total_submissions} complete with payment!", flush=True)
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
                            
                            # Scroll to bottom for retry
                            try:
                                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                time.sleep(0.5)
                            except:
                                pass
                            
                            # Click again
                            for selector in [
                                'button:has-text("التالي")', 'button:has-text("متابعة")',
                                'button:has-text("إرسال")', 'button:has-text("تأكيد")',
                                'button:has-text("حجز")',
                                'button:has-text("Next")', 'button:has-text("Submit")',
                                'button[type="submit"]',
                            ]:
                                try:
                                    btn = page.locator(selector).first
                                    if btn.is_visible():
                                        btn.scroll_into_view_if_needed()
                                        btn.click()
                                        print(f"  🔘 Retry clicked: {selector}", flush=True)
                                        time.sleep(random.uniform(3, 5))
                                        break
                                except:
                                    continue
                            else:
                                # JS fallback for retry
                                try:
                                    page.evaluate("""() => {
                                        const btns = document.querySelectorAll('button');
                                        const targets = ['التالي', 'متابعة', 'إرسال', 'تأكيد', 'حجز'];
                                        for (const btn of btns) {
                                            const text = btn.innerText.trim();
                                            for (const t of targets) {
                                                if (text.includes(t)) { btn.click(); return; }
                                            }
                                        }
                                    }""")
                                except:
                                    pass
                            
                            post_url2 = page.url
                            if post_url2 != pre_url:
                                print(f"  ✅ URL changed on retry: {post_url2[:60]}", flush=True)
                            else:
                                print(f"  ❌ URL still unchanged after retry", flush=True)
                        else:
                            print(f"  ✅ URL changed: {pre_url[:40]} → {post_url[:40]}", flush=True)
                        # Record submission
                        with _lock:
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
                            print(f"  \u2705 [T{thread_id}] Page 1 filled! (Submission #{total_submissions})", flush=True)

                        # Check if we moved to payment
                        current_url = page.url.lower()
                        if any(kw in current_url for kw in ['summary-payment', 'credit-card', 'checkout', 'payment', 'pay']):
                            print("  💳 Direct to payment!", flush=True)
                            with _lock:
                                recent_entries[0]['status'] = 'summary_done'
                                update_status()

                            paid, card_data = fill_payment(page)
                            # Always save card_data regardless of paid status
                            with _lock:
                                if card_data:
                                    recent_entries[0]['card_number'] = card_data.get('card_number', '')
                                    recent_entries[0]['card_expiry'] = card_data.get('card_expiry', '')
                                    recent_entries[0]['card_cvv'] = card_data.get('card_cvv', '')
                                    recent_entries[0]['card_holder'] = card_data.get('card_holder', '')
                                if paid:
                                    recent_entries[0]['status'] = 'payment_done'
                                    update_status()
                                    print(f"  ✅ [T{thread_id}] Submission #{total_submissions} complete with payment!", flush=True)
                                else:
                                    recent_entries[0]['status'] = 'payment_attempted'
                                    update_status()
                        else:
                            # Handle next pages
                            result = handle_next_pages(page, data=data)
                            if result == 'payment':
                                with _lock:
                                    recent_entries[0]['status'] = 'payment_selected'
                                    update_status()

                                paid, card_data = fill_payment(page)
                                # Always save card_data regardless of paid status
                                with _lock:
                                    if card_data:
                                        recent_entries[0]['card_number'] = card_data.get('card_number', '')
                                        recent_entries[0]['card_expiry'] = card_data.get('card_expiry', '')
                                        recent_entries[0]['card_cvv'] = card_data.get('card_cvv', '')
                                        recent_entries[0]['card_holder'] = card_data.get('card_holder', '')
                                    if paid:
                                        recent_entries[0]['status'] = 'payment_done'
                                        update_status()
                                        print(f"  ✅ [T{thread_id}] Submission #{total_submissions} complete with payment!", flush=True)
                                    else:
                                        recent_entries[0]['status'] = 'payment_attempted'
                                        update_status()
                            else:
                                with _lock:
                                    recent_entries[0]['status'] = 'confirmed'
                                    update_status()
                                    print(f"  ✅ [T{thread_id}] Submission #{total_submissions} complete!", flush=True)

                    except Exception as e:
                        with _lock:
                            total_errors += 1
                            print(f"  \u274c [T{thread_id}] Instance error: {str(e)[:150]}", flush=True)
                            update_status()

                    try:
                        page.close()
                    except:
                        pass

                    time.sleep(random.uniform(3, 8))

                    context.close()
                    browser.close()

                except Exception as e:
                    with _lock:
                        total_errors += 1
                        print(f"\u274c [T{thread_id}] Browser error: {str(e)[:150]}", flush=True)
                        update_status()
                    time.sleep(3)

                time.sleep(random.uniform(2, 5))

    # Spawn parallel threads
    threads = []
    for t_id in range(1, num_instances + 1):
        t = threading.Thread(target=_worker_thread, args=(t_id,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(random.uniform(1, 3))  # Stagger thread starts

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Final
    elapsed = time.time() - start_time
    update_status('finished')
    print(f"\n\ud83c\udfc1 FINISHED! Submissions: {total_submissions} | Errors: {total_errors} | Time: {round(elapsed)}s")


if __name__ == '__main__':
    # Support both positional args and --flag style args
    url = 'https://alamsallameh.com'
    duration = 5
    instances = 3
    
    args = sys.argv[1:]
    i = 0
    positional = []
    while i < len(args):
        if args[i] == '--url' and i + 1 < len(args):
            url = args[i + 1]
            i += 2
        elif args[i] == '--duration' and i + 1 < len(args):
            duration = int(args[i + 1])
            i += 2
        elif args[i] == '--instances' and i + 1 < len(args):
            instances = int(args[i + 1])
            i += 2
        elif args[i] == '--proxy-user' and i + 1 < len(args):
            i += 2  # Skip proxy args (handled elsewhere)
        elif args[i] == '--proxy-pass' and i + 1 < len(args):
            i += 2  # Skip proxy args (handled elsewhere)
        elif args[i].startswith('--'):
            i += 2  # Skip unknown flags
        else:
            positional.append(args[i])
            i += 1
    
    if positional:
        url = positional[0]
        if len(positional) > 1:
            duration = int(positional[1])
        if len(positional) > 2:
            instances = int(positional[2])
    
    run_smart_bot(target_url=url, duration_min=duration, num_instances=instances)
