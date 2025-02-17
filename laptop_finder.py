import os
import sys
import numpy as np
import pandas as pd
import streamlit as st


def clickable(cols):
    return f'<a href="{cols.url}">{cols.title}</a>'\
           f'<br/><em>{cols.time}</em>'


def is_new_value(is_new: int, stock: int):
    if not stock:
        return 'HABIS'
    if is_new == 1:
        return 'BARU'
    return 'BEKAS'


def price_value(cols):
    s = '{:0,}'.format(int(cols.price))
    s = s.replace(',', '.')
    s = f'Rp {s}'
    label = is_new_value(cols.is_new, cols.stock)
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
            'laptop.csv',
            'http://warga.web.id/files/dijual/laptop.csv.gz']
    for csv_file in FILES:
        if os.path.exists(csv_file):
            break

COLUMNS = [
    'brand_name', 'title', 'price', 'processor', 'graphic', 'memory',
    'memory_gb', 'storage', 'storage_gb', 'monitor', 'monitor_inch', 'weight',
    'weight_kg', 'is_new', 'processor_name', 'graphic_name', 'graphic_gb',
    'stock', 'description', 'time']

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

DEFAULT = dict(
        price=15000000, memory=8, vram=12, storage=256, monitor=14, weight=1.6,
        graphic='NVIDIA')

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
orig_df = orig_df[orig_df.category == 'laptop']

df = orig_df[orig_df.processor_name.notnull()]
processor_list = [x for x in df.processor_name.drop_duplicates()]
processor_list.sort()

df = orig_df[orig_df.graphic_name.notnull()]
graphic_list = [x for x in df.graphic_name.drop_duplicates()]
graphic_index = default_index('graphic')
graphic_list.sort()

brand_list = [x for x in orig_df.brand_name.drop_duplicates()]
brand_list.sort()

df = orig_df[orig_df.memory_gb.notnull()]
memory_list = [int(x) for x in df.memory_gb.drop_duplicates()]
memory_index = default_index('memory')

df = orig_df[orig_df.graphic_gb.notnull()]
vram_list = [int(x) for x in df.graphic_gb.drop_duplicates()]
vram_index = default_index('vram')

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
df.insert(3, 'price_rp', orig_df.apply(price_value, axis='columns'))
df = df.sort_values(by=['price'])

# Kolom
# 1 nomor, 2 brand_name, 3 title, 4 price, 5 price_rp, 6 processor, 7 graphic,
# 8 memory, 9 memory_gb, 10 storage, 11 storage_gb, 12 monitor,
# 13 monitor_inch, 14 weight, 15 weight_kg, 16 is_new, 17 processor_name,
# 18 graphic_name, 19 graphic_gb, 20 stock, 21 description, 22 time

# Sembunyikan nomor, dan lainnya yang tidak nyaman
hide_columns = [2, 4, 9, 11, 13, 15, 16, 17, 18, 19, 20, 21, 22]
css = """
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
    """
for column in hide_columns:
    css += f'\n    tr>:nth-child({column})' + '{display: none}'
css += '\n</style>'
st.markdown(css, unsafe_allow_html=True)

st.title('Laptop Finder')
if st.checkbox('Brand'):
    choice = st.selectbox('Brand', brand_list)
    df = df[df.brand_name == choice]
if st.checkbox('Processor'):
    choice = st.selectbox('Processor', processor_list)
    df = df[df.processor_name == choice]
if st.checkbox('Graphic'):
    choice = st.selectbox('Graphic', graphic_list, index=graphic_index)
    df = df[df.graphic_name == choice]
if st.checkbox('Minimum VRAM'):
    choice = st.selectbox('GB', vram_list, index=vram_index)
    df = df[df.graphic_gb >= choice]
if st.checkbox('Minimum memory'):
    choice = st.selectbox('GB', memory_list, index=memory_index)
    df = df[df.memory_gb >= choice]
if st.checkbox('SSD'):
    df = df[df.storage.str.contains('ssd', na=False, case=False)]
if st.checkbox('Minimum storage'):
    choice = st.selectbox('GB', storage_list, index=storage_index)
    df = df[df.storage_gb >= choice]
if st.checkbox('Maximum monitor'):
    choice = st.selectbox('Inch', monitor_list, index=monitor_index)
    df = df[df.monitor_inch <= choice]
if st.checkbox('Thunderbolt'):
    df = df[df.description.str.contains('thunderbolt', na=False, case=False)]
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
    df = df[df.stock > 0]
sort_by = st.selectbox(
            'Sort by', options=SORT_BY_KEYS, format_func=sort_by_label)
df = df.sort_values(by=[sort_by], ascending=[ASC[sort_by]])
df = df.replace(np.nan, '', regex=True)
st.write(f'Found {len(df)} rows')
st.write(
    df.to_html(escape=False), unsafe_allow_html=True)
