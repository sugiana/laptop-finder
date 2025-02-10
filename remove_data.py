import sys
import os
from argparse import ArgumentParser
from configparser import ConfigParser
from urllib.parse import urlparse
from glob import glob


pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--csv-only', action='store_true')
option = pars.parse_args(sys.argv[1:])

conf = ConfigParser()
conf.read(option.conf)

cf = dict(conf.items('main'))

csv_files = []
for url in cf['url'].strip().splitlines():
    p = urlparse(url)
    shop_path = p.path.lstrip('/').split('/')[0]
    web_name = p.netloc.split('.')[-2]
    download_dir = '-'.join([web_name, shop_path])
    csv_file = download_dir + '.csv'
    csv_files.append(csv_file)
    if option.csv_only:
        continue
    download_dir = os.path.join(cf['base_download_dir'], download_dir)
    if not os.path.exists(download_dir):
        continue
    for filename in os.listdir(download_dir):
        filename = os.path.join(download_dir, filename)
        print('Hapus', filename)
        os.remove(filename)
    print('Hapus', download_dir)
    os.rmdir(download_dir)
    # Hapus daftar URL produk
    csv_file = download_dir + '.csv'
    if os.path.exists(csv_file):
        os.remove(csv_file)

for filename in csv_files:
    if os.path.exists(filename):
        print('Hapus', filename)
        os.remove(filename)
filename = cf['category'] + '.csv'
if os.path.exists(filename):
    print('Hapus', filename)
    os.remove(filename)
