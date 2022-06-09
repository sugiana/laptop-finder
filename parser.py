import re
from logging import getLogger
from html.parser import HTMLParser
from jaccard_index.jaccard import jaccard_index


C_ALPHABET_PATTERN = re.compile('[a-z]')
NUMERIC_PATTERN = r'(\d+(?:\.\d+)?)'
C_NUMERIC_PATTERN = re.compile(NUMERIC_PATTERN)
COMMA_NUMERIC_PATTERN = r'(\d+(?:,\d+)?)'
C_PARTIAL_PATTERN = re.compile(r'(\S+) :')
MINIMUM_VALUES = dict(
    memory=1, storage=128, monitor=7, weight=0.5, price=2000000)
MAXIMUM_VALUES = dict(memory=32, storage=1024*5, monitor=20, weight=10)
GB_SIZE = dict(m=1/1024, g=1, ssd=1, nvme=1, t=1024)
GB_GROUP = ['memory', 'storage']
INCH_GROUP = ['monitor']
KG_GROUP = ['weight']
MIN_J_INDEX = 0.3

MAPPING_KEYS = [
    ('processor', ['cpu']),
    ('graphic', ['vga', 'integrated gpu', 'tipe grafis']),
    ('memory', ['ram']),
    ('storage', ['internal storage', 'kapasitas penyimpanan', 'hard disk']),
    ('monitor', ['display', 'layar', 'screen', 'panel', 'lcd']),
    ('weight', ['berat', 'bobot', 'weight approximate'])]
INVALID_KEYS = ['amd']

# Jaccard index
MAPPING_VALUES = [
    ('processor', [
        'amd 3020', 'amd ryzen', 'amd athlon', 'amd core', 'apple m1 cpu',
        'intel celeron', 'intel core', 'intel pentium', 'ryzen',
        'tiger lake']),
    ('graphic', [
        'amd radeon', 'intel hd', 'intel iris', 'gpu', 'nvidia',
        'nvidia geforce', 'radeon', 'uhd']),
    ('memory', ['ddr']),
    ('storage', ['ssd', 'nvme']),
    ('monitor', ['inch']),
    ('weight', ['kg'])
    ]
DICT_MAPPING_VALUES = dict(MAPPING_VALUES)
VALID_PROCESSORS = [
    'alder lake', 'amd', 'apple', 'core i', 'intel', 'ryzen', 'tiger lake']

# Regular expression
MAPPING_PARTIAL_VALUES = [
    ('processor', [
        # ?i = insensitive (abaikan perbedaan huruf kecil dan besar)
        r'((?i:amd))( )(\d+)((?i:[a-z]))',
        r'((?i:amd))(.*)((?i:dual))(.*)((?i:core))',
        r'((?i:amd athlon))(.*)( )(\d+)((?i:[a-z]))',
        r'((?i:amd ryzen))(.*)((?i:processor))',
        r'((?i:apple))(.*)((?i:cpu))',
        r'((?i:intel))(.*)((?i:processor))',
        r'((?i:intel))(.*)((?i:i))(\d+)(-)(\d+)((?i:g))(\d+)',
        r'((?i:intel))(.*)((?i:i))(\d+)(-)(\d+)((?i:[a-z]))',
        r'((?i:ryzen))( )(\d+)( )(\d+)((?i:[a-z]))',
        f'{NUMERIC_PATTERN}((?i:ghz))(.*)((?i:core))',
        ]),
    ('graphic', [
        r'((?i:amd radeon))',
        r'((?i:intel))( )(hd|uhd)',
        r'((?i:intel iris xe))',
        r'((?i:iris xe))',
        r'((?i:nvidia))(.*)((?i:mx))(\d+)',
        r'((?i:nvidia))(.*)((?i:rtx))',
        r'((?i:radeon))',
        r'((?i:uhd))',
        r'(\d+)(.*)((?i:core gpu))',
        ]),
    ('memory', [
        r'((?i:ram))(.*)(\d+)((?i:gb))',
        r'(\d+)(.*)((?i:gb))(.*)((?i:ddr))(\d+)(-)(\d+)',
        r'(\d+)((?i:gb))(.*)((?i:memory))',
        r'(\d+)(.*)((?i:gb))(.*)((?i:ddr))(\d+)',
        ]),
    ('storage', [
        r'(\d+)((?i:gb))((?i: pci))(.*)((?i:ssd))',
        r'(\d+)((?i:g))(.*)((?i:storage))',
        r'(\d+)((?i:g))(.*)((?i:ssd))',
        r'(\d+)((?i:g))(.*)((?i:hdd))',
        r'(\d+)((?i:t))(.*)((?i:ssd))',
        r'(\d+)((?i:t))(.*)((?i:hdd))',
        r'(\d+)((?i: g))(.*)((?i:ssd))',
        r'(\d+)((?i: g))(.*)((?i:hdd))',
        r'(\d+)((?i: t))(.*)((?i:ssd))',
        r'(\d+)((?i: t))(.*)((?i:hdd))',
        r'((?i:hdd))( )(\d+)((?i:tb))',
        r'((?i:ssd))(\d+)',
        r'((?i:ssd))( )(\d+)',
        ]),
    ('monitor', [
        f'{NUMERIC_PATTERN}(.*)((?i:inch))(.*)((?i:display))',
        f'{NUMERIC_PATTERN}(.*)((?i:inch))(.*)((?i:fhd))',
        f'{NUMERIC_PATTERN}(.*)((?i:inch))',
        f'{NUMERIC_PATTERN}(")( )((?i:fhd))',
        f'{NUMERIC_PATTERN}( )((?i:hd))',
        f'{NUMERIC_PATTERN}( )((?i:ips))',
        f'{NUMERIC_PATTERN}((?i: ips))',
        r'\(' + f'''{NUMERIC_PATTERN}(")''' + r'\)',
        f'''{NUMERIC_PATTERN}('|"| ") ''',
        f'''{COMMA_NUMERIC_PATTERN}('|"| ") ''',
        ]),
    ]
DICT_MAPPING_PARTIAL_VALUES = dict(MAPPING_PARTIAL_VALUES)

NUMERIC_VALUES = dict(
    memory=[
        r'(\d+) (g)',
        r'(\d+)(g)',
        ],
    storage=[
        r'(\d+)(.*)(ssd)',
        r'(\d+)(.*)(nvme)',
        r'(\d+)(g)',
        r'(\d+)(t)',
        r'(\d+) (g)',
        r'(\d+) (t)',
        ] + DICT_MAPPING_PARTIAL_VALUES['storage'],
    monitor=[
        f'{NUMERIC_PATTERN}',
        f'{COMMA_NUMERIC_PATTERN}',
        ],
    weight=[
        f'{NUMERIC_PATTERN} (kg)',
        f'{COMMA_NUMERIC_PATTERN} (kg)',
        f'{NUMERIC_PATTERN}(kg)',
        f'{COMMA_NUMERIC_PATTERN}(kg)',
        ])


class InvalidBrand(Exception):
    pass


class InvalidProcessor(Exception):
    pass


class InvalidCategory(Exception):
    pass


class InvalidDescription(Exception):
    pass


class HTML2Text(HTMLParser):
    def __init__(self, show_log=True):
        super().__init__()
        self.show_log = show_log
        self.lines = []

    def handle_data(self, data):
        log = getLogger('handle_data')
        s = data.strip()
        if s:
            self.show_log and log.debug(s)
            self.lines.append(s)


def j_index(a: str, b: str) -> float:
    if len(b) < 2:
        return 0
    if C_ALPHABET_PATTERN.search(b):
        return jaccard_index(a, b)
    return 0


def standard_key(orig_key: str) -> str:
    # Agar key menjadi baku. Contoh: RAM menjadi memory.
    if len(orig_key) < 2:
        return
    if orig_key in INVALID_KEYS:
        return
    log = getLogger('standard_key')
    last_index = 0
    last_key = None
    for key, ref_keys in MAPPING_KEYS:
        for ref_key in [key] + ref_keys:
            index = j_index(ref_key, orig_key)
            if index < MIN_J_INDEX:
                continue
            if last_index >= index:
                continue
            last_ref_key = ref_key
            last_index = index
            last_key = key
    if last_key:
        log.debug(
                f'{last_key} {last_ref_key} VS {orig_key} index {last_index}')
    return last_key


def parse_by_separator(lines: list, separator: str) -> list:
    # Contoh:
    # Processor: AMD Ryzen 7
    # Kata pertama adalah key: Processor
    # Kata-kata berikutnya adalah value: AMD Ryzen 7
    log = getLogger('parse_by_separator')
    r = []
    for txt in lines:
        s = txt.lstrip('-').strip()
        if s.find(separator) < 0:
            continue
        t = s.split(separator)
        if not t:
            continue
        orig_key = t[0].strip().lower()
        key = standard_key(orig_key)
        if not key:
            log.warning(
                f'Dengan separator {[separator]} {orig_key} tidak '
                f'ditemukan acuannya')
            continue
        val = separator.join(t[1:]).strip()
        if val:
            log.debug(f'{key} {val}')
            r.append((key, val))
    return r


def parse_by_diff_row(lines: list) -> list:
    # Merangkai key dan value yang berbeda baris. Contoh:
    # Baris pertama adalah key: Processor
    # Baris kedua adalah value: AMD Ryzen 7
    log = getLogger('parse_by_diff_row')
    r = []
    key = None
    for txt in lines:
        if key:
            if txt:
                log.debug(f'{key} {txt}')
                r.append((key, txt))
                key = None
        else:
            new_key = standard_key(txt.lower())
            if not new_key:
                continue
            key = new_key
    return r


def parse_by_pattern(lines: list) -> list:
    # Mendapatkan potongan pola key-value dari sebuah kalimat. Contoh:
    # Kalimat: "Processor : Intel Celeron quad-core processor N5100 "
    #          "OS : Windows 11 Home Memory : 4 GB DDR4"
    # Pola 1: "Processor : Intel Celeron quad-core processor N5100"
    # Pola 2: "OS : Windows 11 Home"
    # Pola 3: "Memory : 4 GB DDR4"
    r = []
    for txt in lines:
        match_list = [m for m in C_PARTIAL_PATTERN.finditer(txt)]
        while match_list:
            match = match_list[0]
            match_list = match_list[1:]
            orig_key = match.group()
            key_pos = match.start()
            val_pos = key_pos + len(orig_key)
            if match_list:
                next_key_pos = match_list[0].start()
                val = txt[val_pos:next_key_pos]
            else:
                val = txt[val_pos:]
            key = standard_key(orig_key.lower())
            if key:
                val = val.strip()
                if val:
                    r.append((key, val))
    return r


def parse_by_jaccard(lines: list) -> list:
    # Mendapatkay key dari value. Contoh:
    # AMD Ryzen 7 -> processor
    # NVIDIA GeForce -> graphic
    # 15.6-inch, FHD (1920 x 1080) -> monitor
    log = getLogger('parse_val_by_jaccard')
    r = []
    for txt in lines:
        s = txt.lower()
        for key, ref_vals in MAPPING_VALUES:
            last_index = 0
            for ref_val in ref_vals:
                index = j_index(ref_val, s)
                if index >= MIN_J_INDEX:
                    last_index = index
                    last_ref_val = ref_val
            if last_index:
                log.debug(f'{key} {last_ref_val} VS {s} index {last_index}')
                r.append((key, txt))
    return r


def parse_partial_vals(lines: list) -> list:
    # Mendapatkan potongan value dari sebuah kalimat. Biasanya kumpulan spec
    # ada di judul. Contoh:
    # Judul: Asus A416EPO-VIPS551 Plus i5-1135G7-MX330-8GB-512GB SSD-Win 10
    # Value: 512GB SSD
    # Key: storage
    log = getLogger('parse_partial_vals')
    r = []
    for txt in lines:
        for key, patterns in MAPPING_PARTIAL_VALUES:
            for pattern in patterns:
                match = re.compile(pattern).search(txt)
                if match:
                    val = ''.join(match.groups())
                    r.append((key, val))
                    log.debug(
                        f'{key} {txt} menjadi {val} sesuai pola {pattern}')
        if txt.find(',') < 0:
            continue
        r += parse_partial_vals(txt.split(','))
    return r


def validate_processor(val: str):
    for word in VALID_PROCESSORS:
        if val.find(word) > -1:
            return
    raise InvalidProcessor()


def value_index(key: str, val: str) -> float:
    # Dapatkan nilai akurasi suatu value.
    log = getLogger('choose')
    if key == 'processor':
        try:
            validate_processor(val)
        except InvalidProcessor:
            log.warning(f'{key} {val} tidak dikenal')
            return 0
    last_index = 0
    for pattern in DICT_MAPPING_VALUES[key]:
        index = j_index(pattern, val)
        if index > last_index:
            last_index = index
            last_pattern = pattern
    if last_index:
        log.debug(f'{key} {last_pattern} VS {val} index {last_index}')
    return last_index


def is_valid_range(key: str, val: str, numeric: float) -> bool:
    log = getLogger('choose')
    if numeric is None:
        log.warning(f'{key} {val} gagal di-float()')
        return
    if key in MINIMUM_VALUES and numeric < MINIMUM_VALUES[key]:
        log.warning(
            f'{key} {val}, {numeric} lebih kecil dari {MINIMUM_VALUES[key]}')
        return
    if key in MAXIMUM_VALUES and numeric > MAXIMUM_VALUES[key]:
        log.warning(
            f'{key} {val}, {numeric} lebih besar dari {MAXIMUM_VALUES[key]}')
        return
    if key == 'storage':
        n = numeric / 128
        if n == int(n):
            return True
        log.warning(f'{key} {val}, {numeric} tidak habis dibagi 128')
        return
    return True


def warning_numeric_not_found(key: str, val: str):
    log = getLogger('get_numeric')
    if C_NUMERIC_PATTERN.search(val):
        log.warning(f'{key} {val} dibuang karena angka tidak dipahami')
    else:
        log.warning(f'{key} {val} dibuang')


def get_numeric(key: str, val: str) -> dict:
    d = dict()
    s = val.lower()
    log = getLogger('choose')
    for pattern in NUMERIC_VALUES[key]:
        match = re.compile(pattern).search(s)
        if not match:
            continue
        for v in match.groups():
            numeric = v.replace(',', '.')
            try:
                numeric = float(numeric)
                break
            except ValueError:
                log.warning(f'{key} {val} = {numeric} gagal di-float')
                numeric = None
                continue
        log.debug(f'{key} {val} = {numeric} berhasil di-float')
        d[key] = val
        if key in GB_GROUP:
            unit = 'g'
            for t in match.groups():
                if t in GB_SIZE:
                    unit = t
                    break
            key_unit = f'{key}_gb'
            d[key_unit] = GB_SIZE[unit] * numeric
        elif key in INCH_GROUP:
            key_unit = f'{key}_inch'
            d[key_unit] = numeric
        else:
            unit = match.group(2).strip().lower()
            key_unit = f'{key}_{unit}'
            d[key_unit] = numeric
        if not is_valid_range(key, val, d[key_unit]):
            continue
        return d
    warning_numeric_not_found(key, val)


def choose(rows_list: list) -> dict:
    log = getLogger('choose')
    d = dict()
    last_index = dict()
    last_priority = dict()
    priority = 0
    for rows in rows_list:
        priority += 1
        for key, val in rows:
            if key in NUMERIC_VALUES:
                if key in d:
                    continue
                new = get_numeric(key, val)
                if new:
                    d.update(new)
            else:
                if key in last_priority and last_priority[key] < priority and \
                        last_index[key] > MIN_J_INDEX:
                    continue
                index = value_index(key, val.lower())
                if key in last_index:
                    old_index = last_index[key]
                    if old_index >= index:
                        continue
                    old_val = d[key]
                    log.warning(
                        f'{key} {old_val} (index {old_index:.2f}) '
                        f'diganti dengan {val} (index {index:.2f})')
                last_index[key] = index
                last_priority[key] = priority
                d[key] = val
    return d


class Parser:
    def __init__(self, response):
        self.response = response

    @classmethod
    def get_product_urls(cls, response) -> list:  # Override, please
        return []

    @classmethod
    def next_page_url(cls, response) -> str:  # Override, please
        pass

    def get_title(self) -> str:  # Override, please
        pass

    def get_brand(self) -> str:
        return self.get_title().split()[0]

    def get_price(self) -> str:  # Override, please
        pass

    def get_url(self) -> str:
        return self.response.url

    def get_info(self, every=2) -> dict:
        lines = []
        for xs in self.response.xpath(self.XPATH_INFO):
            s = xs.extract()
            p = HTML2Text(True)
            p.feed(s)
            lines += p.lines
        lines = [lines[x:x+every] for x in range(0, len(lines), every)]
        d = dict()
        for t in lines:
            key = t[0]
            val = t[-1]
            key = key.split(':')[0]
            d[key] = val
        return d

    def validate_category(self):
        for ref_category in ('laptop', 'notebook'):
            if self.info['Kategori'].lower().find(ref_category) > -1:
                return
        raise InvalidCategory()

    def parse(self) -> dict:
        self.info = self.get_info()
        self.validate_category()
        d = dict()
        d['brand'] = self.get_brand()
        d['title'] = self.get_title()
        d['price'] = self.get_price()
        xs = self.response.xpath(self.XPATH_DESC)
        s = xs.extract()[0]
        p = HTML2Text()
        p.feed(s)
        rows_list = []  # Skala prioritas
        rows_list.append(parse_by_separator(p.lines, ':'))
        rows_list.append(parse_by_separator(p.lines, ' '))
        rows_list.append(parse_by_diff_row(p.lines))
        rows_list.append(parse_by_pattern(p.lines))
        rows_list.append(parse_by_jaccard(p.lines))
        title = self.get_title()
        rows_list.append(parse_partial_vals(p.lines + [title]))
        desc = choose(rows_list)
        if not desc:
            raise InvalidDescription()
        d.update(desc)
        return d
