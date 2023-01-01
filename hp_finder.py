import sys
import os
import numpy as np
import pandas as pd
import streamlit as st


def title_value(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'


def price_value(n):
    s = '{:0,}'.format(int(n))
    s = s.replace(',', '.')
    return f'Rp {s}'


def nfc_value(n):
    if n == '0':
        return ''
    if n.lower().find('nfc') > -1:
        return n
    return f'NFC {n}'


def compass_value(n):
    if n == '0':
        return ''
    if n.lower().find('compass') > -1:
        return n
    return n


def network_5g_value(n):
    if n == '0':
        return ''
    return n


csv_file = None
for argv in sys.argv[1:]:
    if argv[-4:] == '.csv':
        csv_file = argv

if not csv_file:
    FILES = [
        'hp-all.csv', 'hp.csv', 'http://warga.web.id/files/dijual/hp.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break

COLUMNS = [
    'brand', 'title', 'price', 'processor', 'graphic', 'memory', 'memory_gb',
    'storage', 'storage_gb', 'monitor', 'monitor_inch', 'battery',
    'battery_mah', 'network_5g', 'nfc', 'usb', 'usb_c', 'compass', 'weight',
    'weight_kg']
GRAPHICS = ['Adreno', 'PowerVR']

SORT_BY = dict(
    price='Price',
    memory_gb='Memory',
    storage_gb='Storage',
    monitor='Monitor',
    weight_kg='Weight')
SORT_BY_KEYS = list(SORT_BY.keys())
ASC = dict(
        price=True, memory_gb=False, storage_gb=False, monitor=True,
        weight_kg=True)

DEFAULT = dict(price=2500000, memory=4, storage=128, monitor=6, weight=0.15)

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


@st.cache(ttl=60*60*24)
def read_csv():
    return pd.read_csv(csv_file)


orig_df = read_csv()

brand_list = [x for x in orig_df.brand.drop_duplicates()]
brand_list.sort()

df = orig_df[orig_df.memory_gb.notnull()]
memory_list = [int(x) for x in df.memory_gb.drop_duplicates()]
memory_index = default_index('memory')

df = orig_df[orig_df.storage_gb.notnull()]
storage_list = [int(x) for x in df.storage_gb.drop_duplicates()]
storage_index = default_index('storage')

df = orig_df[orig_df.monitor_inch.notnull()]
monitor_list = [x for x in df.monitor_inch.drop_duplicates()]
monitor_index = default_index('monitor')

df = orig_df[orig_df.weight_kg.notnull()]
df = df[df.weight_kg > 0]
weight_list = [x for x in df.weight_kg.drop_duplicates()]
weight_index = default_index('weight')

price_step = 500000
price_min = int(orig_df.price.min() / price_step + 1) * price_step
price_max = int(orig_df.price.max() / price_step + 1) * price_step

df = orig_df[COLUMNS].copy()
df['title'] = orig_df.apply(title_value, axis='columns')
df['nfc'] = df['nfc'].apply(nfc_value)
df['compass'] = df['compass'].apply(compass_value)
df['network_5g'] = df['network_5g'].apply(network_5g_value)
df.insert(3, 'price_rp', df['price'].apply(price_value))
df = df.sort_values(by=['price'])

# Kolom
# 1 nomor, 2 brand, 3 title, 4 price, 5 price_rp, 6 processor, 7 graphic,
# 8 memory, 9 memory_gb, 10 storage, 11 storage_gb, 12 monitor,
# 13 monitor_inch, 14 battery, 15 battery_mah, 16 network_5g, 17 nfc,
# 18 usb, 19 usb_c, 20 compass, 21 weight, 22 weight_kg

# Sembunyikan nomor, dan lainnya yang tidak nyaman
hide_columns = [2, 4, 9, 11, 13, 15, 19, 22]
css = '''
    <style>
    .block-container {max-width: 100rem}
    th {display: none}
    td {vertical-align: top}'''
for column in hide_columns:
    css += f'\n    tr>:nth-child({column})' + '{display: none}'
css += '\n</style>'
st.markdown(css, unsafe_allow_html=True)

st.title('HP Finder')
if st.checkbox('Brand filter'):
    brand_choice = st.selectbox('Brand', brand_list)
    df = df[df.brand == brand_choice]
if st.checkbox('Graphic filter'):
    graphic_choice = st.selectbox('Graphic', GRAPHICS)
    df = df[df.graphic.str.contains(graphic_choice, na=False, case=False)]
if st.checkbox('Minimum memory'):
    memory_choice = st.selectbox('GB', memory_list, index=memory_index)
    df = df[df.memory_gb >= memory_choice]
if st.checkbox('Minimum storage'):
    storage_choice = st.selectbox('GB', storage_list, index=storage_index)
    df = df[df.storage_gb >= storage_choice]
if st.checkbox('Maximum monitor'):
    monitor_choice = st.selectbox('Inch', monitor_list, index=monitor_index)
    df = df[df.monitor_inch <= monitor_choice]
if st.checkbox('5G'):
    df = df[df.network_5g.str.contains('5g', na=False, case=False)]
if st.checkbox('NFC'):
    df = df[df.nfc.str.contains('nfc', na=False, case=False)]
if st.checkbox('USB Type-C'):
    df = df[df.usb_c.notnull()]
if st.checkbox('Compass'):
    df = df[df.compass.str.contains('compass', na=False, case=False)]
if st.checkbox('Maximum weight'):
    weight_choice = st.selectbox('Kg', weight_list, index=weight_index)
    df = df[df.weight_kg <= weight_choice]
if st.checkbox('Maximum price'):
    price_choice = st.slider(
            'Rp', price_min, price_max, DEFAULT['price'], price_step)
    df = df[df.price <= price_choice]
sort_by = st.selectbox(
            'Sort by', options=SORT_BY_KEYS, format_func=sort_by_label)
df = df.sort_values(by=[sort_by], ascending=[ASC[sort_by]])
df = df.replace(np.nan, '', regex=True)
st.write(f'Found {len(df)} rows')
st.write(
    df.to_html(escape=False), unsafe_allow_html=True)
