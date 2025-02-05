import sys
import re
import pandas as pd
from tools import (
    nice_str,
    value2keys,
    clean_data,
    similarity_search,
    )


BRANDS = ['Apple', 'ASUS', 'Infinix', 'Nokia', 'Oppo', 'realme', 'Samsung',
          'Vivo', 'Xiaomi']
BRAND_ALIAS = dict(
    Apple=['IPHONE'],
    Vivo=['GIRI', 'IQOO', 'S1', 'V40', 'Y03', 'Y17', 'Y19', 'Y91C', 'Y93',
          'Y95'],
    Xiaomi=['POCO', 'REDMI'])
brand_back_ref = value2keys(BRAND_ALIAS)

PROCESSOR_BRANDS = ['Apple', 'IMG', 'JLQ', 'MediaTek', 'Qualcomm', 'Samsung',
                    'UNISOC']
lower_processors = {s.lower(): s for s in PROCESSOR_BRANDS}

PROCESSOR_ALIAS = dict(
    ARM=['MALI'],
    IMG=['POWERVR'],
    JLQ=['JR510'],
    MediaTek=['DIMENSITY', 'HELIO', 'MT', 'MTK', 'SNAPDRAGON'],
    Samsung=['EXYNOS'],
    UNISOC=['SC9863A'])
processor_back_ref = value2keys(PROCESSOR_ALIAS)

GRAPHIC_BRANDS = ['ARM', 'IMG', 'MediaTek', 'Qualcomm']
lower_graphics = {s.lower(): s for s in GRAPHIC_BRANDS}

GRAPHIC_ALIAS = dict(
    ARM=['IMMORTALIS', 'MALI', 'MALLI'],
    IMG=['POWERVR'],
    MediaTek=['HELIO', 'G80'],
    Qualcomm=['ADRENO', 'SNAPDRAGON'])
graphic_back_ref = value2keys(GRAPHIC_ALIAS)

RE_NONE = re.compile('TIDAK|NOT MENTION|NONE|UNKNOWN')


def clean_brands(data: dict):
    for column in ['brand', 'processor_brand', 'graphic_brand']:
        value = data[column]
        if value and not pd.isnull(value):
            value = value.upper()
            if RE_NONE.search(value):
                s = 'LAINNYA'
            else:
                s = value.strip().replace('.', '')
                if column == 'graphic_brand':
                    s = similarity_search(s, lower_graphics)
                elif column == 'processor_brand':
                    s = similarity_search(s, lower_processors)
            data[column] = s
    clean_data(data, 'brand', BRANDS, brand_back_ref)
    clean_data(data, 'processor_brand', PROCESSOR_BRANDS, processor_back_ref)
    clean_data(data, 'graphic_brand', GRAPHIC_BRANDS, graphic_back_ref)


NUMERIC_COLUMNS = ['monitor_inch', 'memory_gb', 'storage_gb', 'weight_kg',
                   'battery_mah', 'camera_mp', 'camera_aperture']


def clean_numeric(data: dict):
    for column in NUMERIC_COLUMNS:
        try:
            float(data[column])
        except ValueError:
            data[column] = None


BOOLEAN_COLUMNS = ['usb_c', 'nfc', 'network_5g', 'camera_ois']


def clean_boolean(data: dict):
    for column in BOOLEAN_COLUMNS:
        value = data[column]
        if not pd.isnull(value) and isinstance(value, str):
            value = value.lower()
            data[column] = value.find('ya') == 0 and 1 or 0


BOOLEAN_STR_COLUMNS = ['compass']


def clean_boolean_str(data: dict):
    for column in BOOLEAN_STR_COLUMNS:
        value = data[column]
        if not pd.isnull(value):
            value = value.lower()
            if value.find('tidak') == 0:
                data[column] = None


def repair(csv_file: str):
    df = pd.read_csv(csv_file)
    rows = dict()
    for column in df.columns:
        rows[column] = []
    for index, row in df.iterrows():
        data = dict(row)
        clean_brands(data)
        clean_numeric(data)
        clean_boolean(data)
        clean_boolean_str(data)
        for column in df.columns:
            value = data[column]
            rows[column].append(value)
    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False)


def main(argv=sys.argv[1:]):
    csv_file = argv[0]
    repair(csv_file)


if __name__ == '__main__':
    main()
