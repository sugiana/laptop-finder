import sys
import numpy as np
import pandas as pd
import streamlit as st


def clickable(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'


def price(n):
    s = '{:0,}'.format(int(n))
    s = s.replace(',', '.')
    return f'Rp {s}'


URL = 'http://warga.web.id/files/dijual/laptop.csv.gz'
COLUMNS = [
    'brand', 'title', 'price', 'processor', 'graphic', 'memory', 'memory_gb',
    'storage', 'storage_gb', 'monitor', 'monitor_inch', 'weight', 'weight_kg']
GRAPHICS = ['NVIDIA', 'AMD Radeon', 'Intel Iris']

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

DEFAULT = dict(price=15000000, memory=8, storage=256, monitor=14, weight=1.6)

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
    return pd.read_csv(URL)


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
df['title'] = orig_df.apply(clickable, axis='columns')
df.insert(3, 'price_rp', df['price'].apply(price))
df = df.sort_values(by=['price'])

# Sembunyikan nomor, brand, price, storage_gb, monitor_inch, dan weight_kg
css = """
    <style>
    .block-container {max-width: 100rem}
    th {display: none}
    td {vertical-align: top}
    tr>:nth-child(2){display: none}
    tr>:nth-child(4){display: none}
    tr>:nth-child(9){display: none}
    tr>:nth-child(11){display: none}
    tr>:nth-child(13){display: none}
    tr>:nth-child(15){display: none}
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

st.title('Laptop Finder')
if st.checkbox('Brand filter'):
    brand_choice = st.selectbox('Brand', brand_list)
    df = df[df.brand == brand_choice]
if st.checkbox('Graphic filter'):
    graphic_choice = st.selectbox('Graphic', GRAPHICS)
    df = df[df.graphic.str.contains(graphic_choice, na=False, case=False)]
if st.checkbox('Minimum memory'):
    memory_choice = st.selectbox('GB', memory_list, index=memory_index)
    df = df[df.memory_gb >= memory_choice]
if st.checkbox('SSD'):
    df = df[df.storage.str.contains('ssd', na=False, case=False)]
if st.checkbox('Minimum storage'):
    storage_choice = st.selectbox('GB', storage_list, index=storage_index)
    df = df[df.storage_gb >= storage_choice]
if st.checkbox('Maximum monitor'):
    monitor_choice = st.selectbox('Inch', monitor_list, index=monitor_index)
    df = df[df.monitor_inch <= monitor_choice]
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
