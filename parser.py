import re
from logging import getLogger
from html.parser import HTMLParser
from jaccard_index.jaccard import jaccard_index


C_ALPHABET_PATTERN = re.compile('[a-z]')
NUMERIC_PATTERN = r'(\d+(?:\.\d+)?)'
C_NUMERIC_PATTERN = re.compile(NUMERIC_PATTERN)
COMMA_NUMERIC_PATTERN = r'(\d+(?:,\d+)?)'
C_PARTIAL_PATTERN = re.compile(r'(\S+) :')
C_BRAND_PATTERN = re.compile(r'^(\S+) ((?i:by)) (\S+)')

GB_SIZE = dict(m=1/1024, g=1, ssd=1, nvme=1, t=1024)
KG_SIZE = dict(g=1/1000, kg=1)
GB_GROUP = ['memory', 'storage']
KG_GROUP = ['weight']
INCH_GROUP = ['monitor']
THOUSAND_GROUP = ['battery']

MIN_J_INDEX = 0.3


class InvalidCategory(Exception):
    pass


class InvalidDescription(Exception):
    pass


class InvalidValue(Exception):
    pass


class HTML2Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []

    def handle_data(self, data):
        log = getLogger('handle_data')
        s = data.strip()
        if s:
            s = ' '.join(s.split())
            log.debug(s)
            self.lines.append(s)


def j_index(a: str, b: str) -> float:
    if len(b) < 2:
        return 0
    if C_ALPHABET_PATTERN.search(b):
        return jaccard_index(a, b)
    return 0


def get_numeric(texts):
    for text in texts:
        s = text.replace(',', '.')
        try:
            return float(s)
        except ValueError:
            pass


def get_thousand(texts):
    for separator in ('.', ','):
        for text in texts:
            s = text.replace(separator, '')
            try:
                return int(s)
            except ValueError:
                pass


def get_unit(units, unit_size, default):
    for t in units:
        if t in unit_size:
            return t
    return default


def warning_numeric_not_found(key: str, val: str):
    log = getLogger('choose')
    if C_NUMERIC_PATTERN.search(val):
        log.warning(f'{key} {val} dibuang karena angka tidak dipahami')
    else:
        log.warning(f'{key} {val} dibuang')


class Parser:
    BRANDS = []
    MAPPING_BRANDS = dict()
    VALID_VALUES = dict()
    VALID_WORDS = dict()
    FALSE_VALUES = dict()
    MAPPING_VALUES = dict()
    NUMERIC_MULTIPLE = dict()

    def __init__(self, response):
        self.response = response
        self.VALID_BRANDS = [[x.lower(), x] for x in self.BRANDS]
        self.VALID_BRANDS = dict(self.VALID_BRANDS)

    @classmethod
    def get_product_urls(cls, response) -> list:  # Override, please
        return []

    @classmethod
    def next_page_url(cls, response) -> str:  # Override, please
        pass

    def get_title(self) -> str:  # Override, please
        pass

    def get_brand(self) -> str:
        title = self.get_title()
        match = C_BRAND_PATTERN.search(title)
        if match:
            return match.group(3)
        last_index = 0
        for b in title.split()[:2]:
            b_lower = b.lower()
            if b_lower in self.VALID_BRANDS:
                return self.VALID_BRANDS[b_lower]
            t_lower = title.lower()
            for ref_brand in self.MAPPING_BRANDS:
                if t_lower.find(ref_brand) == 0:
                    return self.MAPPING_BRANDS[ref_brand]
            for ref_brand in self.VALID_BRANDS:
                index = j_index(ref_brand, b_lower)
                if index < MIN_J_INDEX:
                    continue
                if last_index >= index:
                    continue
                last_index = index
                last_brand = ref_brand
        if last_index:
            return self.VALID_BRANDS[last_brand]
        return b

    def get_price(self) -> str:  # Override, please
        pass

    def get_url(self) -> str:
        return self.response.url

    def get_info(self, every=2) -> dict:
        lines = []
        for xs in self.response.xpath(self.XPATH_INFO):
            s = xs.extract()
            p = HTML2Text()
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
        if 'Kategori' in self.info:
            for ref_category in self.CATEGORIES:
                if self.info['Kategori'].lower().find(ref_category) > -1:
                    return
        raise InvalidCategory()

    def validate_value(self, key: str, val: str):
        if key in self.VALID_WORDS:
            for w in self.VALID_WORDS[key]:
                for found in re.findall(r'([a-zA-Z0-9]*)', val):
                    if found == w:
                        return
        elif key in self.VALID_VALUES:
            for w in self.VALID_VALUES[key]:
                if val.find(w) > -1:
                    return
        else:
            return
        raise InvalidValue()

    def standard_key(self, orig_key: str) -> str:
        # Agar key menjadi baku. Contoh: RAM menjadi memory.
        if len(orig_key) < 2:
            return
        if orig_key in self.INVALID_KEYS:
            return
        log = getLogger('standard_key')
        last_index = 0
        last_key = None
        orig_key = orig_key.lower()
        for key, ref_keys in self.MAPPING_KEYS:
            for ref_key in [key] + ref_keys:
                index = j_index(ref_key, orig_key)
                if index < MIN_J_INDEX:
                    continue
                if last_index >= index:
                    continue
                if len(ref_key) < 4 and orig_key.find(ref_key) < 0:
                    continue
                last_ref_key = ref_key
                last_index = index
                last_key = key
        if last_key:
            log.debug(
                f'{last_key} {last_ref_key} VS {orig_key} index {last_index}')
        return last_key

    def parse_table(self, rows: list) -> list:
        # Contoh:
        # Kolom pertama: Processor
        # Kolom kedua: Snapdragon
        log = getLogger('parse_table')
        r = []
        for orig_key, val in rows:
            key = self.standard_key(orig_key)
            if not key:
                log.warning(
                    f'{orig_key} tidak ditemukan acuannya')
                continue
            val = val.strip()
            if val:
                log.debug(f'{key} {val}')
                r.append((key, val))
        return r

    def parse_by_separator(self, lines: list, separator: str) -> list:
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
            if separator.strip():
                t = s.split(separator)
            else:
                t = s.split()
            if not t:
                continue
            orig_key = t[0].strip().lower()
            key = self.standard_key(orig_key)
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

    def parse_by_separator_2(self, lines: list, sep1: str, sep2: str) -> list:
        # Mendapatkan potongan pola "keys values" dari sebuah kalimat. Contoh:
        # RAM/ROM 4 GB/64 GB
        # Ram/ Rom: 6/ 64GB
        log = getLogger('parse_by_separator_2')
        r = []
        for txt in lines:
            s = txt.lstrip('-').strip()
            if s.find(sep1) < 0:
                continue
            if sep1.strip():
                t = s.split(sep1)
            else:
                t = s.split()
            if not t:
                continue
            orig_keys = t[0].strip().lower().split(sep2)
            vals = sep1.join(t[1:]).split(sep2)
            if len(orig_keys) != len(vals):
                continue
            i = -1
            for orig_key in orig_keys:
                i += 1
                key = self.standard_key(orig_key)
                if not key:
                    log.warning(
                        f'Dengan separator {[sep2]} {orig_key} tidak '
                        f'ditemukan acuannya')
                    continue
                val = vals[i]
                log.debug(f'{key} {val}')
                r.append((key, val))
        return r

    def parse_by_diff_row(self, lines: list) -> list:
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
                new_key = self.standard_key(txt)
                if not new_key:
                    continue
                key = new_key
        return r

    def parse_by_pattern(self, lines: list) -> list:
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
                key = self.standard_key(orig_key)
                if key:
                    val = val.strip()
                    if val:
                        r.append((key, val))
        return r

    def parse_by_jaccard(self, lines: list) -> list:
        # Mendapatkay key dari value. Contoh:
        # AMD Ryzen 7 -> processor
        # NVIDIA GeForce -> graphic
        # 15.6-inch, FHD (1920 x 1080) -> monitor
        log = getLogger('parse_val_by_jaccard')
        r = []
        for txt in lines:
            s = txt.lower()
            for key in self.MAPPING_VALUES:
                ref_vals = self.MAPPING_VALUES[key]
                last_index = 0
                for ref_val in ref_vals:
                    index = j_index(ref_val, s)
                    if index >= MIN_J_INDEX:
                        last_index = index
                        last_ref_val = ref_val
                if last_index:
                    log.debug(
                        f'{key} {last_ref_val} VS {s} index {last_index}')
                    r.append((key, txt))
        return r

    def parse_partial_vals(self, lines: list) -> list:
        # Mendapatkan potongan value dari sebuah kalimat. Biasanya kumpulan
        # spec ada di judul. Contoh:
        # Judul: Asus A416EPO-VIPS551 Plus i5-1135G7-MX330-8GB-512GB SSD-Win 10
        # Value: 512GB SSD
        # Key: storage
        log = getLogger('parse_partial_vals')
        r = []
        for txt in lines:
            for key, patterns in self.MAPPING_PARTIAL_VALUES:
                for pattern in patterns:
                    match = re.compile(pattern).search(txt)
                    if match:
                        val = ''.join(match.groups())
                        r.append((key, val))
                        log.debug(
                            f'{key} {txt} menjadi {val} sesuai pola {pattern}')
            if txt.find(',') < 0:
                continue
            r += self.parse_partial_vals(txt.split(','))
        return r

    def is_valid_range(self, key: str, val: str, numeric: float) -> bool:
        log = getLogger('choose')
        if numeric is None:
            log.warning(f'{key} {val} gagal di-float()')
            return
        if key in self.MINIMUM_VALUES and numeric < self.MINIMUM_VALUES[key]:
            log.warning(
                f'{key} {val}, {numeric} lebih kecil dari '
                f'{self.MINIMUM_VALUES[key]}')
            return
        if key in self.MAXIMUM_VALUES and numeric > self.MAXIMUM_VALUES[key]:
            log.warning(
                f'{key} {val}, {numeric} lebih besar dari '
                f'{self.MAXIMUM_VALUES[key]}')
            return
        if key in self.NUMERIC_MULTIPLE:
            m = self.NUMERIC_MULTIPLE[key]
            n = numeric / m
            if n == int(n):
                return True
            log.warning(f'{key} {val}, {numeric} tidak habis dibagi {m}')
            return
        return True

    def get_numeric(self, key: str, val: str) -> dict:
        d = dict()
        s = val.lower()
        log = getLogger('choose')
        for pattern in self.NUMERIC_VALUES[key]:
            match = re.compile(pattern).search(s)
            if not match:
                continue
            texts = match.groups()
            if key in THOUSAND_GROUP:
                numeric = get_thousand(texts)
            else:
                numeric = get_numeric(texts)
            log.debug(
                f'{key} {val} = {numeric} berhasil di-float sesuai '
                f'pola {pattern}')
            d[key] = val
            if key in GB_GROUP:
                unit = get_unit(texts, GB_SIZE, 'g')
                key_unit = f'{key}_gb'
                d[key_unit] = GB_SIZE[unit] * numeric
            elif key in KG_GROUP:
                unit = get_unit(texts, KG_SIZE, 'kg')
                key_unit = f'{key}_kg'
                d[key_unit] = KG_SIZE[unit] * numeric
            elif key in INCH_GROUP:
                key_unit = f'{key}_inch'
                d[key_unit] = numeric
            else:
                unit = match.group(2).strip().lower()
                key_unit = f'{key}_{unit}'
                d[key_unit] = numeric
            if not self.is_valid_range(key, val, d[key_unit]):
                continue
            return d
        warning_numeric_not_found(key, val)

    def value_index(self, key: str, val: str) -> float:
        # Dapatkan nilai akurasi suatu value.
        log = getLogger('choose')
        try:
            self.validate_value(key, val)
        except InvalidValue:
            log.warning(f'{key} {val} tidak dikenal')
            return 0
        last_index = 0
        ref_vals = []
        if key in self.VALID_VALUES:
            ref_vals += self.VALID_VALUES[key]
        if key in self.MAPPING_VALUES:
            ref_vals += self.MAPPING_VALUES[key]
        for ref_val in ref_vals:
            index = j_index(ref_val, val)
            if index > last_index:
                last_index = index
                last_ref_val = ref_val
        if last_index:
            log.debug(f'{key} {last_ref_val} VS {val} index {last_index}')
        return last_index

    def choose(self, rows_list: list) -> dict:
        log = getLogger('choose')
        d = dict()
        last_index = dict()
        last_priority = dict()
        priority = 0
        for rows in rows_list:
            priority += 1
            for key, val in rows:
                if key in self.NUMERIC_VALUES:
                    if key in d:
                        continue
                    new = self.get_numeric(key, val)
                    new and d.update(new)
                else:
                    if key in last_priority and \
                            last_priority[key] < priority and \
                            last_index[key] > MIN_J_INDEX:
                        continue
                    if key in self.FALSE_VALUES:
                        for ref_val in self.FALSE_VALUES[key]:
                            if val.lower().find(ref_val) > -1:
                                d[key] = 0
                                last_index[key] = last_priority[key] = 1
                                continue
                    index = self.value_index(key, val.lower())
                    if not index:
                        continue
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

    def parse_custom(self, lines: list) -> list:
        return []

    def parse(self) -> dict:
        self.info = self.get_info()
        self.validate_category()
        d = dict()
        d['brand'] = self.get_brand()
        d['title'] = self.get_title()
        d['price'] = self.get_price()
        if isinstance(self.XPATH_DESC, str):
            xs = self.response.xpath(self.XPATH_DESC)
            s = xs.extract()[0]
        else:
            s = self.XPATH_DESC()
        p = HTML2Text()
        p.feed(s)
        rows_list = []  # Skala prioritas
        rows_list.append(self.parse_by_separator(p.lines, ':'))
        rows_list.append(self.parse_by_separator(p.lines, ' '))
        rows_list.append(self.parse_by_separator_2(p.lines, ' ', '/'))
        rows_list.append(self.parse_by_separator_2(p.lines, ':', '/'))
        rows_list.append(self.parse_by_diff_row(p.lines))
        rows_info = [(key, self.info[key]) for key in self.info]
        rows_list.append(self.parse_table(rows_info))
        rows_list.append(self.parse_by_pattern(p.lines))
        rows_list.append(self.parse_by_jaccard(p.lines))
        lines = p.lines + [self.get_title()]
        rows_list.append(self.parse_partial_vals(lines))
        custom_list = self.parse_custom(lines)
        custom_list and rows_list.append(custom_list)
        desc = self.choose(rows_list)
        if not desc:
            raise InvalidDescription()
        for key in self.FALSE_VALUES:
            if key not in desc:
                desc[key] = 0
        d.update(desc)
        return d
