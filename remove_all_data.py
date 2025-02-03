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

if not option.csv_only:
    for url in cf['url'].strip().splitlines():
        p = urlparse(url)
        shop_path = p.path.lstrip('/').split('/')[0]
        web_name = p.netloc.split('.')[-2]
        download_dir = '-'.join([web_name, shop_path])
        download_dir = os.path.join(cf['base_download_dir'], download_dir)
        if not os.path.exists(download_dir):
            continue
        for filename in os.listdir(download_dir):
            filename = os.path.join(download_dir, filename)
            print('Hapus', filename)
            os.remove(filename)
        print('Hapus', download_dir)
        os.rmdir(download_dir)

for filename in glob(f'{cf["category"]}-*.csv'):
    print('Hapus', filename)
    os.remove(filename)
