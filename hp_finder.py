import sys
import os
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title='Cari handphone')


def get_list(column: str, cast_func=None):
    c = getattr(orig_df, column)
    tmp_df = orig_df[c.notnull()]
    c = getattr(tmp_df, column)
    if cast_func:
        list_ = [cast_func(x) for x in c.drop_duplicates()]
    else:
        list_ = [x for x in c.drop_duplicates()]
    list_.sort()
    if column in DEFAULT:
        index = -1
        for val in list_:
            index += 1
            if val >= DEFAULT[column]:
                break
    else:
        index = 0
    return list_, index


def filter_name(column, label):
    list_, index = get_list(column)
    choice = st.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c == choice]


def filter_boolean(column):
    c = getattr(df, column)
    return df[c.notnull()]


def filter_min(column: str, label: str, cast_func=None) -> pd.DataFrame:
    list_, index = get_list(column, cast_func)
    choice = st.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c >= choice]


def filter_max(column: str, label: str) -> pd.DataFrame:
    list_, index = get_list(column)
    choice = st.selectbox(label, list_, index=index)
    c = getattr(df, column)
    return df[c <= choice]


def get_title(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'\
           f'<br/><em>{cols.time}</em>'


def get_is_new(is_new: int, stock: int):
    if not stock:
        return 'HABIS'
    if is_new == 1:
        return 'BARU'
    return 'BEKAS'


def get_price(cols):
    s = '{:0,}'.format(int(cols.price))
    s = s.replace(',', '.')
    s = f'Rp {s}'
    label = get_is_new(cols.is_new, cols.stock)
    if label:
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


def sort_by_label(key):
    return SORT_BY[key]


COLUMNS = [
        'title', 'price', 'processor', 'memory', 'camera', 'monitor',
        'is_usb_c']
SORT_BY = dict(
    price='Price', memory_gb='Memory', storage_gb='Storage',
    monitor_inch='Monitor', camera_mp='Camera pixel',
    camera_aperture='Camera aperture', weight_kg='Weight')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(
        price=True, memory_gb=False, storage_gb=False, monitor_inch=True,
        weight_kg=True, camera_mp=False, camera_aperture=True)
DEFAULT = dict(
            price=2500000, memory_gb=4, storage_gb=128, monitor_inch=6,
            weight_kg=0.15, camera_mp=50, camera_aperture=1.8)

csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
        'hp.csv', 'http://warga.web.id/files/dijual/hp.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break


@st.cache_data(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()
orig_df = orig_df[orig_df.category == 'hp']
df = orig_df.copy()

st.title('Handphone')
if st.checkbox('Brand'):
    df = filter_name('brand_name', 'Brand')

if st.checkbox('Processor'):
    df = filter_name('processor_name', 'Processor')

if st.checkbox('Graphic'):
    df = filter_name('graphic_name', 'Graphic')

if st.checkbox('Minimum memory'):
    df = filter_min('memory_gb', 'GB', int)

if st.checkbox('Minimum storage'):
    df = filter_min('storage_gb', 'GB', int)

if st.checkbox('Minimum camera pixel'):
    df = filter_min('camera_mp', 'Megapixel', int)

if st.checkbox('Minimum camera aperture'):
    df = filter_max('camera_aperture', 'f/n')

if st.checkbox('Optical Image Stabilization'):
    df = filter_boolean('is_camera_ois')

if st.checkbox('Maximum monitor'):
    df = filter_max('monitor_inch', 'Inch')

if st.checkbox('5G'):
    df = filter_boolean('is_network_5g')

if st.checkbox('NFC'):
    df = filter_boolean('is_nfc')

if st.checkbox('USB Type-C'):
    df = filter_boolean('is_usb_c')

if st.checkbox('Compass'):
    df = filter_boolean('is_compass')

if st.checkbox('Maximum weight'):
    df = filter_max('weight_kg', 'Kg')

if st.checkbox('Maximum price'):
    step = 500000
    tmp_df = orig_df[orig_df.stock > 0]
    min_ = int(tmp_df.price.min() / step + 1) * step
    max_ = int(tmp_df.price.max() / step + 1) * step
    choice = st.slider('Rp', min_, max_, DEFAULT['price'], step)
    df = df[df.price <= choice]

if st.checkbox('New'):
    df = df[df.is_new == 1]

if st.checkbox('Stock'):
    df = df[df.stock > 1]

choice = st.selectbox(
        'Sort by', options=SORT_BY_KEYS, format_func=sort_by_label)
if choice != 'price':
    c = getattr(df, choice)
    df = df[c.notnull()]
df = df.sort_values(by=[choice], ascending=[ASC[choice]])

count = len(df)
if count:
    df = df.replace(np.nan, '', regex=True)
    tmp_df = df[COLUMNS].copy()
    tmp_df['title'] = df.apply(get_title, axis='columns')
    tmp_df['price'] = df.apply(get_price, axis='columns')
    tmp_df['processor'] = df.apply(get_processor, axis='columns')
    tmp_df['memory'] = df.apply(get_memory, axis='columns')
    tmp_df['monitor'] = df.apply(get_monitor, axis='columns')
    tmp_df['camera'] = df.apply(get_camera, axis='columns')
    tmp_df['is_usb_c'] = df.apply(get_usb, axis='columns')
    st.write(f'Found {count} rows')
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
    </style>'''
    st.markdown(css, unsafe_allow_html=True)
    st.write(tmp_df.to_html(escape=False), unsafe_allow_html=True)
else:
    st.write('No result')
