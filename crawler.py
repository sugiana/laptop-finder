import sys
import os
from argparse import ArgumentParser
from urllib.parse import urlparse
from downloader import Browser
from to_csv import to_csv
from to_category import parse
from tools import read_conf
from repair import repair
from csv_concat import concat


pars = ArgumentParser()
pars.add_argument('conf')
pars.add_argument('--do-not-download', action='store_true')
option = pars.parse_args(sys.argv[1:])

cf = read_conf(option.conf)
if not (base_download_dir := cf.get('base_download_dir')):
    home_dir = os.path.expanduser('~')
    base_download_dir = os.path.join(home_dir, 'tmp')
    if not os.path.exists(base_download_dir):
        print('Create', base_download_dir)
        os.mkdir(base_download_dir)

download_dirs = []
for url in cf['url'].strip().splitlines():
    print(url)
    p = urlparse(url)
    web_path = p.path.lstrip('/').replace('/', '-')
    web_name = p.netloc.split('.')[-2]
    download_dir = '-'.join([web_name, web_path])
    download_dir = os.path.join(base_download_dir, download_dir)
    download_dirs.append((web_name, download_dir))
    print('  Download Directory:', download_dir)
    if not os.path.exists(download_dir):
        print('  Create', download_dir)
        os.mkdir(download_dir)
    if option.do_not_download:
        continue
    a = Browser(url, download_dir, cf['is_ready_stock'])
    a.run()

csv_sources = []
for web_name, download_dir in download_dirs:
    output_file = os.path.split(download_dir)[-1] + '.csv'
    print(f'{download_dir} -> {output_file}')
    to_csv(web_name, download_dir, output_file)
    csv_sources.append(output_file)

for csv_source in csv_sources:
    if not os.path.exists(csv_source):
        continue
    name, ext = os.path.splitext(csv_source)
    output_file = [cf['category']] + name.split('-')[1:]
    output_file = '-'.join(output_file) + ext
    parse(cf, csv_source, output_file)
    if os.path.exists(output_file):
        repair(cf, output_file)
        concat(cf['category'])
