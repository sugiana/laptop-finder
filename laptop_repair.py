import sys
import pandas as pd
from tools import (
    nice_str,
    value2keys,
    clean_data,
    )


BRANDS = ['Acer', 'Apple', 'ASUS', 'Axioo', 'Dell', 'HP', 'Lenovo', 'MSI',
          'Toshiba', 'Zyrex']
BRAND_ALIAS = dict(Apple=['MACBOOK'], Dell=['LATITUDE'], Zyrex=['MAVERIC'])
brand_back_ref = value2keys(BRAND_ALIAS)

PROCESSOR_BRANDS = ['AMD', 'Apple', 'Intel', 'MediaTek', 'Qualcomm']
PROCESSOR_ALIAS = dict(
    AMD=['RYZEN'],
    Apple=['M2', 'M2 PRO', 'M3', 'M3 PRO', 'M4'],
    Qualcomm=['SNAPDRAGON'])
processor_back_ref = value2keys(PROCESSOR_ALIAS)

GRAPHIC_BRANDS = ['AMD', 'Apple', 'Intel', 'NVIDIA', 'Qualcomm', 'Radeon']
GRAPHIC_ALIAS = dict(
    AMD=['VEGA'],
    Apple=['M2', 'M3'],
    NVIDIA=['GEFORCE', 'RTX'],
    Intel=['HD', 'INTEGRATED', 'IRIS', 'UHD', 'UMA'])
graphic_back_ref = value2keys(GRAPHIC_ALIAS)


def clean_category(data: dict):
    if data['category'] != 'laptop':
        return
    value = data['processor']
    if pd.isnull(value):
        return
    if value.lower().find('tidak') > -1:
        data['category'] = 'lainnya'


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
    clean_data(data, 'processor_brand', PROCESSOR_BRANDS, processor_back_ref)
    clean_data(data, 'graphic_brand', GRAPHIC_BRANDS, graphic_back_ref)


NUMERIC_COLUMNS = ['memory_gb', 'storage_gb', 'graphic_gb', 'monitor_inch',
                   'weight_kg']


def clean_numeric(data: dict):
    for column in NUMERIC_COLUMNS:
        try:
            float(data[column])
        except ValueError:
            data[column] = None


def repair(csv_file):
    df = pd.read_csv(csv_file)
    rows = dict()
    for column in df.columns:
        rows[column] = []
    for index, row in df.iterrows():
        data = dict(row)
        clean_category(data)
        clean_brands(data)
        clean_numeric(data)
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
