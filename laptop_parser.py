from logging import getLogger
from parser import (
    NUMERIC_PATTERN,
    COMMA_NUMERIC_PATTERN,
    Parser as Base,
    )


class Parser(Base):
    CATEGORIES = ['laptop', 'notebook']
    BRANDS = [
        'Acer', 'Apple', 'Asus', 'Dell', 'HP', 'Lenovo', 'MSI', 'Toshiba']
    MAPPING_BRANDS = {
        'laptop gaming msi': 'MSI',
        'legion': 'Lenovo',
        'macbook': 'Apple',
        }
    MINIMUM_VALUES = dict(
        memory=1, storage=128, monitor=7, weight=0.5, price=2000000)
    MAXIMUM_VALUES = dict(memory=32, storage=1024*5, monitor=20, weight=10)
    NUMERIC_MULTIPLE = dict(storage=128)
    # Jaccard index untuk menetapkan key
    MAPPING_KEYS = [
        ('processor', ['cpu']),
        ('graphic', ['vga', 'integrated gpu', 'tipe grafis']),
        ('memory', ['ram']),
        ('storage', ['internal storage', 'kapasitas penyimpanan',
                     'hard disk']),
        ('monitor', ['display', 'layar', 'screen', 'panel', 'lcd']),
        ('weight', ['berat', 'bobot', 'weight approximate'])]
    INVALID_KEYS = ['amd']
    # Jaccard index untuk menetapkan value
    MAPPING_VALUES = dict(
        graphic=[
            'amd radeon', 'intel hd', 'intel iris', 'gpu', 'nvidia',
            'nvidia geforce', 'radeon', 'uhd'],
        memory=['ddr'],
        storage=['ssd', 'nvme'],
        monitor=['inch'],
        weight=['kg'])
    # Nilai ini juga disertakan dalam Jaccard index. Setelah diperoleh index
    # tertinggi tetap dicari apakah memuat kata yang terdapat di VALID_VALUES.
    VALID_VALUES = dict(
        processor=[
            'alder lake', 'amd', 'apple m1', 'comet lake', 'core i', 'i7',
            'intel', 'ryzen', 'tiger lake'])
    # Regular expression
    MAPPING_PARTIAL_VALUES = [
        ('processor', [
            # ?i = insensitive (abaikan perbedaan huruf kecil dan besar)
            r'((?i:amd))( )(\d+)((?i:[a-z]))',
            r'((?i:amd))(.*)((?i:dual))(.*)((?i:core))',
            r'((?i:amd athlon))(.*)( )(\d+)((?i:[a-z]))',
            r'((?i:amd ryzen))(.*)((?i:processor))',
            r'((?i:apple))(.*)((?i:cpu))',
            r'((?i:core i))(\d)',
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
