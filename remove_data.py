import sys
import os
from argparse import ArgumentParser
from urllib.parse import urlparse
from glob import glob
from tools import read_conf


pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--csv-only', action='store_true')
option = pars.parse_args(sys.argv[1:])

cf = read_conf(option.conf)
if not (base_download_dir := cf.get('base_download_dir')):
    home_dir = os.path.expanduser('~')
    base_download_dir = os.path.join(home_dir, 'tmp')

csv_files = []
for url in cf['url'].strip().splitlines():
    p = urlparse(url)
    web_path = p.path.lstrip('/').replace('/', '-')
    web_name = p.netloc.split('.')[-2]
    download_dir = '-'.join([web_name, web_path])
    html_csv_file = download_dir + '.csv'
    csv_files.append(html_csv_file)
    category_csv_file = '-'.join([cf['category'], web_path]) + '.csv'
    csv_files.append(category_csv_file)
    if option.csv_only:
        continue
    download_dir = os.path.join(base_download_dir, download_dir)
    if not os.path.exists(download_dir):
        continue
    for filename in os.listdir(download_dir):
        filename = os.path.join(download_dir, filename)
        print('Hapus', filename)
        os.remove(filename)
    print('Hapus', download_dir)
    os.rmdir(download_dir)
    url_csv_file = download_dir + '.csv'
    if os.path.exists(url_csv_file):
        print('Hapus', url_csv_file)
        os.remove(url_csv_file)

for filename in csv_files:
    if os.path.exists(filename):
        print('Hapus', filename)
        os.remove(filename)
filename = cf['category'] + '.csv'
if os.path.exists(filename):
    print('Hapus', filename)
    os.remove(filename)
