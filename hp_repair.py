import sys
import pandas as pd
from tools import (
    nice_str,
    value2keys,
    clean_data,
    )


BRANDS = ['Apple', 'ASUS', 'Infinix', 'Nokia', 'Oppo', 'realme', 'Samsung',
          'Vivo', 'Xiaomi']
BRAND_ALIAS = dict(
    Apple=['IPHONE'],
    Vivo=['GIRI', 'IQOO', 'S1', 'V40', 'Y03', 'Y17', 'Y19', 'Y91C', 'Y93',
          'Y95'],
    Xiaomi=['POCO', 'REDMI'])
brand_back_ref = value2keys(BRAND_ALIAS)

PROCESSOR_BRANDS = ['IMG', 'MediaTek', 'Qualcomm']

GRAPHIC_BRANDS = ['ARM', 'IMG', 'Qualcomm']
GRAPHIC_ALIAS = dict(
    ARM=['IMMORTALIS', 'MALI'],
    IMG=['POWERVR'],
    Qualcomm=['ADRENO'])
graphic_back_ref = value2keys(GRAPHIC_ALIAS)


def clean_brands(data: dict):
    for column in ['brand', 'processor_brand', 'graphic_brand']:
        value = data[column]
        if value and not pd.isnull(value):
            value = value.upper()
            if value.find('TIDAK') == 0:
                s = 'LAINNYA'
            else:
                s = value.strip().replace('.', '')
            data[column] = s
    clean_data(data, 'brand', BRANDS, brand_back_ref)
    clean_data(data, 'processor_brand', PROCESSOR_BRANDS)
    clean_data(data, 'graphic_brand', GRAPHIC_BRANDS, graphic_back_ref)


NUMERIC_COLUMNS = ['monitor_inch', 'memory_gb', 'storage_gb', 'weight_kg',
                   'battery_mah']


def clean_numeric(data: dict):
    for column in NUMERIC_COLUMNS:
        try:
            float(data[column])
        except ValueError:
            data[column] = None


BOOLEAN_COLUMNS = ['usb_c', 'nfc', 'network_5g']


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
