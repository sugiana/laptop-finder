import sys
import os
import numpy as np
import pandas as pd
import streamlit as st


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

COLUMNS = [
    'brand_name', 'title', 'price', 'processor', 'graphic', 'memory',
    'memory_gb', 'storage', 'storage_gb', 'monitor', 'monitor_inch', 'battery',
    'battery_mah', 'is_network_5g', 'is_nfc', 'usb', 'is_usb_c', 'is_compass',
    'weight', 'weight_kg', 'is_new', 'stock', 'processor_name',
    'graphic_name', 'camera', 'camera_mp', 'camera_aperture', 'is_camera_ois']

SORT_BY = dict(
    price='Price',
    memory_gb='Memory',
    storage_gb='Storage',
    monitor='Monitor',
    camera_mp='Camera pixel',
    camera_aperture='Camera aperture',
    weight_kg='Weight')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(
        price=True, memory_gb=False, storage_gb=False, monitor=True,
        weight_kg=True, camera_mp=False, camera_aperture=True)

DEFAULT = dict(price=2500000, memory=4, storage=128, monitor=6, weight=0.15,
               camera_mp=50, camera_aperture=1.8)

MAIN = sys.modules[__name__]


def default_index(name):
    index = 0
    vals = getattr(MAIN, f'{name}_list')
    vals.sort()
    for val in vals:
        if val >= DEFAULT[name]:
            break
        index += 1
    return index


def sort_by_label(key):
    return SORT_BY[key]


@st.cache_data(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()
orig_df = orig_df[orig_df.category == 'hp']
choice_df = orig_df[orig_df.stock > 0]

brand_list = [x for x in choice_df.brand_name.drop_duplicates()]
brand_list.sort()

df = choice_df[choice_df.processor_name.notnull()]
processor_list = [x for x in df.processor_name.drop_duplicates()]
processor_list.sort()

df = choice_df[choice_df.graphic_name.notnull()]
graphic_list = [x for x in df.graphic_name.drop_duplicates()]
graphic_list.sort()

df = choice_df[choice_df.memory_gb.notnull()]
memory_list = [int(x) for x in df.memory_gb.drop_duplicates()]
memory_index = default_index('memory')

df = choice_df[choice_df.storage_gb.notnull()]
storage_list = [int(x) for x in df.storage_gb.drop_duplicates()]
storage_index = default_index('storage')

df = choice_df[choice_df.monitor_inch.notnull()]
monitor_list = [x for x in df.monitor_inch.drop_duplicates()]
monitor_index = default_index('monitor')

df = choice_df[choice_df.weight_kg.notnull()]
df = df[df.weight_kg > 0]
weight_list = [x for x in df.weight_kg.drop_duplicates()]
weight_index = default_index('weight')

df = choice_df[choice_df.camera_mp.notnull()]
df = df[df.camera_mp > 0]
camera_mp_list = [int(x) for x in df.camera_mp.drop_duplicates()]
camera_mp_index = default_index('camera_mp')

df = choice_df[choice_df.camera_aperture.notnull()]
df = df[df.camera_aperture > 0]
camera_aperture_list = [x for x in df.camera_aperture.drop_duplicates()]
camera_aperture_index = default_index('camera_aperture')

price_step = 500000
price_min = int(choice_df.price.min() / price_step + 1) * price_step
price_max = int(choice_df.price.max() / price_step + 1) * price_step

df = orig_df[COLUMNS].copy()
df['title'] = orig_df.apply(get_title, axis='columns')
df.insert(3, 'price_rp', orig_df.apply(get_price, axis='columns'))
df = df.sort_values(by=['price'])

# Kolom
# 1 nomor, 2 brand_name, 3 title, 4 price, 5 price_rp, 6 processor, 7 graphic,
# 8 memory, 9 memory_gb, 10 storage, 11 storage_gb, 12 monitor,
# 13 monitor_inch, 14 battery, 15 battery_mah, 16 network_5g, 17 is_nfc,
# 18 usb, 19 is_usb_c, 20 is_compass, 21 weight, 22 weight_kg, 23 is_new,
# 24 stock, 25 processor_name, 26 graphic_name, 27 camera, 28 camera_mp,
# 29 camera_aperture, 30 is_camera_ois

# Sembunyikan nomor, dan lainnya yang tidak nyaman
hide_columns = [2, 4, 9, 11, 13, 15, 19, 22, 23, 24, 25, 26, 28, 29, 30]
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
    }'''
for column in hide_columns:
    css += f'\n    tr>:nth-child({column})' + '{display: none}'
css += '\n</style>'
st.markdown(css, unsafe_allow_html=True)

st.title('HP Finder')
if st.checkbox('Brand'):
    choice = st.selectbox('Brand', brand_list)
    df = df[df.brand_name == choice]
if st.checkbox('Processor'):
    choice = st.selectbox('Processor', processor_list)
    df = df[df.processor_name == choice]
if st.checkbox('Graphic'):
    choice = st.selectbox('Graphic', graphic_list)
    df = df[df.graphic_name == choice]
if st.checkbox('Minimum memory'):
    choice = st.selectbox('GB', memory_list, index=memory_index)
    df = df[df.memory_gb >= choice]
if st.checkbox('Minimum storage'):
    choice = st.selectbox('GB', storage_list, index=storage_index)
    df = df[df.storage_gb >= choice]
if st.checkbox('Camera pixel'):
    choice = st.selectbox(
        'Megapixel', camera_mp_list, index=camera_mp_index)
    df = df[df.camera_mp <= choice]
if st.checkbox('Camera aperture'):
    choice = st.selectbox('f/n', camera_aperture_list)
    df = df[df.camera_aperture <= choice]
if st.checkbox('Optical Image Stabilization'):
    df = df[df.is_camera_ois.notnull()]
if st.checkbox('Maximum monitor'):
    choice = st.selectbox('Inch', monitor_list, index=monitor_index)
    df = df[df.monitor_inch <= choice]
if st.checkbox('5G'):
    df = df[df.is_network_5g.notnull()]
if st.checkbox('NFC'):
    df = df[df.is_nfc.notnull()]
if st.checkbox('USB Type-C'):
    df = df[df.is_usb_c.notnull()]
if st.checkbox('Compass'):
    df = df[df.is_compass.notnull()]
if st.checkbox('Maximum weight'):
    choice = st.selectbox('Kg', weight_list, index=weight_index)
    df = df[df.weight_kg <= choice]
if st.checkbox('Maximum price'):
    choice = st.slider(
            'Rp', price_min, price_max, DEFAULT['price'], price_step)
    df = df[df.price <= choice]
if st.checkbox('New'):
    df = df[df.is_new == 1]
if st.checkbox('Stock'):
    df = df[df.stock > 1]
sort_by = st.selectbox(
            'Sort by', options=SORT_BY_KEYS, format_func=sort_by_label)
df = df.sort_values(by=[sort_by], ascending=[ASC[sort_by]])
df = df.replace(np.nan, '', regex=True)
st.write(f'Found {len(df)} rows')
st.write(
    df.to_html(escape=False), unsafe_allow_html=True)
