import sys
import os
import pandas as pd
import numpy as np
import streamlit as st


def get_list(column: str, cast_func=None):
    c = getattr(orig_df, column)
    tmp_df = orig_df[c.notnull()]
    c = getattr(tmp_df, column)
    if cast_func:
        list_ = [cast_func(x) for x in c.drop_duplicates()]
    else:
        list_ = [x for x in c.drop_duplicates()]
    list_.sort()
    if column in DEFAULT[category]:
        index = -1
        for val in list_:
            index += 1
            if val >= DEFAULT[category][column]:
                break
    else:
        index = 0
    return list_, index


def filter_name(column, label):
    list_, index = get_list(column)
    choice = st.sidebar.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c == choice]


def filter_contains(column, label):
    text = st.sidebar.text_input(label)
    c = getattr(df, column)
    return df[c.str.contains(text, na=False, case=False)]


def filter_boolean(column):
    c = getattr(df, column)
    return df[c.notnull()]


def filter_min(column: str, label: str, cast_func=None) -> pd.DataFrame:
    list_, index = get_list(column, cast_func)
    choice = st.sidebar.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c >= choice]


def filter_max(column: str, label: str) -> pd.DataFrame:
    list_, index = get_list(column)
    choice = st.sidebar.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c <= choice]


def get_title(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'\
           f'<br/><em>{cols.time}</em>'


def get_is_new(cols):
    if not cols.stock:
        return 'HABIS'
    if cols.is_new == 1:
        return 'BARU'
    return 'BEKAS'


def get_price(cols):
    s = '{:0,}'.format(int(cols.price))
    s = s.replace(',', '.')
    s = f'Rp {s}'
    label = get_is_new(cols)
    cls = ['c-label']
    if cols.stock:
        if cols.is_new:
            cls.append('c-label--green')
    else:
        cls.append('c-label--pink')
    cls = ' '.join(cls)
    s += f'<div class="{cls}">{label}</div>'
    return s


def intersect_columns(cols, names: list):
    c1 = getattr(cols, names[0])
    if not c1:
        return ''
    rows = [c1]
    for name in names[1:]:
        c = getattr(cols, name)
        if not c:
            continue
        if c1.find(c) < 0:
            rows.append(c)
    return '<br/>'.join(rows)


def get_memory(cols):
    return intersect_columns(cols, ('memory', 'storage'))


def get_camera(cols):
    return intersect_columns(cols, ('camera', 'is_camera_ois'))


def concat_columns(cols, names: list):
    rows = []
    for column in names:
        try:
            v = getattr(cols, column)
            v = v.strip()
            if v:
                rows.append(v)
        except AttributeError:
            pass
    return '<br/>'.join(rows)


def get_processor(cols):
    return concat_columns(cols, ('processor', 'graphic'))


def get_monitor(cols):
    return concat_columns(cols, ('monitor', 'weight', 'battery'))


def get_usb(cols):
    return concat_columns(
        cols, ('is_network_5g', 'is_nfc', 'is_usb_c', 'is_compass'))


def get_pcie(cols):
    if pd.isnull(cols.pcie_version) or not cols.pcie_version:
        return ''
    return f'PCIe {int(cols.pcie_version)}'


def get_capacity(cols):
    if pd.isnull(cols.capacity_gb) or not cols.capacity_gb:
        return ''
    return f'{int(cols.capacity_gb)} GB'


def get_warranty(cols):
    if pd.isnull(cols.warranty_year) or not cols.warranty_year:
        return ''
    return f'{int(cols.warranty_year)} tahun'


def get_power(cols):
    if pd.isnull(cols.power_watt):
        return ''
    return f'{int(cols.power_watt)} Watt'


COLUMNS = dict(
    laptop=[
        'title', 'price', 'processor', 'memory', 'monitor'],
    hp=[
        'title', 'price', 'processor', 'memory', 'camera', 'monitor',
        'is_usb_c'],
    mobo=['title', 'price', 'pcie_x16'],
    gpu=['title', 'price', 'processor_name', 'memory_gb', 'pcie_version'],
    storage=['title', 'price', 'capacity_gb', 'warranty_year', 'pcie_version'],
    psu=['title', 'price', 'power_watt', 'model_name'])

DEFAULT = dict(
    laptop=dict(
        price=15000000, memory_gb=8, graphic_gb=12, storage_gb=256,
        monitor_inch=14, weight_kg=1.6, graphic_name='NVIDIA'),
    hp=dict(
        price=2500000, memory_gb=4, storage_gb=128, monitor_inch=6,
        weight_kg=0.15, camera_mp=50, camera_aperture=1.8),
    mobo=dict(price=5000000, pcie_x16_count=4, pcie_x16_version=4),
    gpu=dict(
        price=5000000, memory_gb=8, pcie_version=4, processor_name='NVIDIA'),
    storage=dict(
        price=5000000, capacity_gb=1000, warranty_year=5, pcie_version=4),
    psu=dict(price=4000000, power_watt=1000, model_name='Platinum'))

# field = (label, is ascending)
SORT_BY = dict(
    laptop=dict(
        price=('Price', True),
        memory_gb=('Memory', False),
        storage_gb=('Storage', False),
        monitor=('Monitor', True),
        weight_kg=('Weight', True)),
    hp=dict(
        price=('Price', True),
        memory_gb=('Memory', False),
        storage_gb=('Storage', False),
        monitor=('Monitor', True),
        camera_mp=('Camera pixel', False),
        camera_aperture=('Camera aperture', True),
        weight_kg=('Weight', True)),
    mobo=dict(
        price=('Price', True),
        pcie_x16_count=('PCIe x16 count', False),
        pcie_x16_version=('PCIe x16 version', False)),
    gpu=dict(
        price=('Price', True),
        memory_gb=('Memory', False),
        pcie_version=('PCIe', False)),
    storage=dict(
        price=('Price', True),
        capacity_gb=('Capacity', False),
        warranty_year=('Warranty', False),
        pcie_version=('PCIe', False)),
    psu=dict(
        price=('Price', True),
        power_watt=('Watt', False)))

TITLE = dict(
        laptop='Laptop', hp='Handphone', mobo='Motherboard',
        gpu='Graphic Processor Unit', storage='Storage',
        psu='Power Supply Unit')

csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
            'all.csv',
            'http://warga.web.id/files/dijual/all.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break


@st.cache_data(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()
choice = st.sidebar.selectbox(
    'Category', ('Laptop', 'HP', 'Mobo', 'GPU', 'Storage', 'PSU'))
category = choice.lower()
orig_df = orig_df[orig_df.category == category]
df = orig_df.copy()

st.title(TITLE[category])
if st.sidebar.checkbox('Brand'):
    df = filter_name('brand_name', 'Brand')

if category in ('laptop', 'hp', 'gpu'):
    if st.sidebar.checkbox('Processor name'):
        df = filter_name('processor_name', 'Processor')

    if category == 'gpu':
        if st.sidebar.checkbox('Processor model'):
            df = filter_contains('processor_type', 'Any text, ex: 3060')

        if st.sidebar.checkbox('PCIe'):
            df = filter_min('pcie_version', 'Version', int)

    if st.sidebar.checkbox('Minimum memory'):
        df = filter_min('memory_gb', 'GB', int)

    if category in ('laptop', 'hp'):
        if st.sidebar.checkbox('Graphic'):
            df = filter_name('graphic_name', 'Graphic')

        if st.sidebar.checkbox('Minimum storage'):
            df = filter_min('storage_gb', 'GB', int)

        if st.sidebar.checkbox('Maximum monitor'):
            df = filter_max('monitor_inch', 'Inch')

        if st.sidebar.checkbox('Maximum weight'):
            df = filter_max('weight_kg', 'Kg')

        if category == 'hp':
            if st.sidebar.checkbox('Minimum camera pixel'):
                df = filter_min('camera_mp', 'Megapixel', int)

            if st.sidebar.checkbox('Minimum camera aperture'):
                df = filter_max('camera_aperture', 'f/n')

            if st.sidebar.checkbox('Optical Image Stabilization'):
                df = filter_boolean('is_camera_ois')

            if st.sidebar.checkbox('5G'):
                df = filter_boolean('is_network_5g')

            if st.sidebar.checkbox('NFC'):
                df = filter_boolean('is_nfc')

            if st.sidebar.checkbox('USB Type-C'):
                df = filter_boolean('is_usb_c')

            if st.sidebar.checkbox('Compass'):
                df = filter_boolean('is_compass')

elif category == 'mobo':
    if st.sidebar.checkbox('PCIe x16 count'):
        df = filter_min('pcie_x16_count', 'Amount', int)

    if st.sidebar.checkbox('PCIe x16 version'):
        df = filter_min('pcie_x16_version', 'Number', int)

elif category == 'storage':
    if st.sidebar.checkbox('Minimum capacity'):
        df = filter_min('capacity_gb', 'GB', int)

    if st.sidebar.checkbox('PCIe'):
        df = filter_min('pcie_version', 'Version', int)

    if st.sidebar.checkbox('Minimum warranty'):
        df = filter_min('warranty_year', 'Year', int)

elif category == 'psu':
    if st.sidebar.checkbox('Minimum power'):
        df = filter_min('power_watt', 'Watt', int)

    if st.sidebar.checkbox('Model'):
        df = filter_name('model_name', 'Name')

if st.sidebar.checkbox('Maximum price'):
    default = DEFAULT[category]['price']
    step = 500000
    tmp_df = orig_df[orig_df.stock > 0]
    min_ = int(tmp_df.price.min() / step + 1) * step
    max_ = int(tmp_df.price.max() / step + 1) * step
    choice = st.sidebar.slider('Rp', min_, max_, default, step)
    df = df[df.price <= choice]

if st.sidebar.checkbox('New'):
    df = df[df.is_new == 1]

if st.sidebar.checkbox('Stock'):
    df = df[df.stock > 0]

sort_options = SORT_BY[category]
options = list(sort_options.keys())
sort_by = st.sidebar.selectbox(
        'Sort by', options=options,
        format_func=lambda key: sort_options[key][0])
df = df.sort_values(by=[sort_by], ascending=sort_options[sort_by][1])
df = df.replace(np.nan, '', regex=True)

count = len(df)
if count:
    columns = COLUMNS[category]
    tmp_df = df[columns].copy()
    tmp_df['title'] = df.apply(get_title, axis='columns')
    tmp_df['price'] = df.apply(get_price, axis='columns')
    if category in ('laptop', 'hp'):
        tmp_df['processor'] = df.apply(get_processor, axis='columns')
        tmp_df['memory'] = df.apply(get_memory, axis='columns')
        tmp_df['monitor'] = df.apply(get_monitor, axis='columns')
        if category == 'hp':
            tmp_df['camera'] = df.apply(get_camera, axis='columns')
            tmp_df['is_usb_c'] = df.apply(get_usb, axis='columns')
    elif category in ('gpu', 'storage'):
        tmp_df['pcie_version'] = df.apply(get_pcie, axis='columns')
        if category == 'storage':
            tmp_df['capacity_gb'] = df.apply(get_capacity, axis='columns')
            tmp_df['warranty_year'] = df.apply(get_warranty, axis='columns')
    elif category == 'psu':
        tmp_df['power_watt'] = df.apply(get_power, axis='columns')
    css = '''
        <style>
        .block-container {max-width: 100rem}
        th {display: none}
        td {vertical-align: top}
        .c-label {
            height: 18px;
            padding: 1px 6px;
            margin: 0;
            overflow: visible;
            line-height: 14px;
            vertical-align: middle;
            background-color: #fafafa;
            border: 1px solid #ddd;
            border-radius: 2px;
        }
        .c-label--pink {
            background-color: #ff566a;
        }
        .c-label--green {
            background-color: #3cff33;
        }
        '''
    st.markdown(css, unsafe_allow_html=True)
    st.write(f'Found {count} rows')
    st.write(tmp_df.to_html(index=False, escape=False), unsafe_allow_html=True)
else:
    st.write(f'No result')
