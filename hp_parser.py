import re
from parser import (
    NUMERIC_PATTERN,
    COMMA_NUMERIC_PATTERN,
    Parser as Base,
    MIN_J_INDEX,
    j_index,
    )
from laptop_parser import Parser as Base


USB_C_VALUES = ('fast charge', 'supervooc', 'type-c')


class Parser(Base):
    CATEGORIES = ['android']
    BRANDS = [
        'Infinix', 'Oppo', 'Nokia', 'Realme', 'Samsung', 'Vivo', 'Xiaomi']
    MAPPING_BRANDS = {
        'hp samsung': 'Samsung',
        }
    FALSE_VALUES = dict(
        compass=['e-compass'],
        nfc=['n/a', 'no', 'tidak'])
    MINIMUM_VALUES = dict(
        memory=1, storage=16, monitor=5, battery=1000, price=700000)
    MAXIMUM_VALUES = dict(memory=12, storage=1024, monitor=8, weight=0.22)
    NUMERIC_MULTIPLE = dict(storage=16)
    # Jaccard index untuk menetapkan key
    MAPPING_KEYS = [
        ('processor', ['cpu']),
        ('graphic', ['gpu']),
        ('memory', ['memory size', 'ram']),
        ('storage', ['internal memory', 'rom', 'penyimpanan']),
        ('monitor', ['display', 'tampilan', 'ukuran layar']),
        ('weight', ['berat']),
        ('battery', ['pengisian daya', 'type li-po']),
        ('usb', [
            'interface', 'kabel usb', 'pengisian daya type-c', 'power combo']),
        ('nfc', []),
        ('compass', ['sensors']),
        ]
    # Jaccard index untuk menetapkan value
    MAPPING_VALUES = dict(
        processor=['dimensity', 'octa core'],
        monitor=['inch'],
        battery=['mah'],
        usb=['micro usb', 'vooc', 'pengisian daya type-c', 'type-c'])
    # Nilai ini juga disertakan dalam Jaccard index. Setelah diperoleh index
    # tertinggi tetap dicari apakah memuat kata yang terdapat di VALID_VALUES.
    VALID_VALUES = dict(
        processor=[
            'cortex', 'dimensity', 'exynos', 'helio', 'mediatek', 'mt', 'octa',
            'sdm', 'snapdragon', 'unisoc'],
        graphic=['adreno', 'powervr'],
        usb=['fast charge', 'micro usb', 'vooc', 'tipe-c', 'type-c', 'usb 2'],
        nfc=['didukung', 'nfc', 'yes'],
        compass=['compass'])
    # Regular expression
    MAPPING_PARTIAL_VALUES = [
        ('processor', [
            r'((?i:snapdragon))( )(\d+)((?i:[a-z]))',
            ]),
        ('memory', [
            r'(\d+)((?i:gb))(.*)((?i:ram))',
            r'((?i:ram))(.*)(\d+)((?i:gb))',
            ]),
        ('storage', [
            r'(\d+)((?i:gb))( )((?i:rom))',
            r'((?i:rom))( )(\d+) ((?i:gb))',
            r'((?i:rom))( )(\d+)((?i:gb))',
            r'(\d+)((?i:gb))',
            ]),
        ('monitor', [
            f'''{NUMERIC_PATTERN}('|"| ") ''',
            f'''{COMMA_NUMERIC_PATTERN}('|"| ") ''',
            ]),
        ('usb', ['((?i:supervooc))']),
        ('nfc', ['((?i:nfc))']),
        ]
    DICT_MAPPING_PARTIAL_VALUES = dict(MAPPING_PARTIAL_VALUES)
    NUMERIC_VALUES = dict(
        memory=[
            r'ram (\d+)/',
            r'(\d+) (g)',
            r'(\d+)(g)',
            r'^(\d+)$',
            ],
        storage=[
            r'(\d+)(g)',
            r'(\d+) (g)',
            r'^(\d+)$',
            ],
        monitor=[
            f'{NUMERIC_PATTERN} in',
            f'{COMMA_NUMERIC_PATTERN} in',
            f'{NUMERIC_PATTERN}',
            f'{COMMA_NUMERIC_PATTERN}',
            ],
        weight=[
            f'{NUMERIC_PATTERN}(g)',
            f'{NUMERIC_PATTERN} (g)',
            r'(\d+)(g)',
            r'(\d+) (g)',
            ],
        battery=[
            f'{NUMERIC_PATTERN} (mah)',
            f'{COMMA_NUMERIC_PATTERN} (mah)',
            f'{NUMERIC_PATTERN}(mah)',
            f'{COMMA_NUMERIC_PATTERN}(mah)',
            r'(\d+) (mah)',
            r'(\d+)(mah)',
            ]
        )

    def parse_custom(self, lines: list) -> list:  # Override
        keys = ('memory', 'storage')
        # 4 GB 128 GB
        regex = re.compile(r'(\d+)((?i:gb))')
        r = []
        for line in lines:
            i = -1
            for match in regex.finditer(line):
                i += 1
                key = keys[i:] and keys[i]
                if not key:
                    break
                r.append((key, match.group()))
            # Ram/Rom : 4/128 GB
            t = line.split(':')
            if len(t) != 2:
                continue
            orig_keys, vals = t
            orig_keys = orig_keys.split('/')
            vals = vals.split('/')
            if len(orig_keys) != len(vals):
                continue
            i = -1
            for orig_key in orig_keys:
                i += 1
                key = self.standard_key(orig_key)
                if not key:
                    continue
                r.append((key, vals[i].strip()))
        return r

    def choose(self, rows_list: list) -> dict:  # Override
        d = super().choose(rows_list)
        if 'usb' in d:
            s = d['usb'].lower()
            last_index = 0
            for ref_val in USB_C_VALUES:
                if s.find(ref_val) > -1:
                    last_index = 1
                    break
                index = j_index(ref_val, s)
                if index >= MIN_J_INDEX:
                    last_index = index
            if last_index:
                d['usb_c'] = d['usb']
        return d
