import sys
import os
from argparse import ArgumentParser
from configparser import ConfigParser
from urllib.parse import urlparse
from downloader import Browser
from to_csv import to_csv
from to_category import parse as base_parse
from to_category_by_gemini import parse as gemini_parse
from laptop_repair import repair as laptop_repair
from hp_repair import repair as hp_repair
from csv_concat import concat


REPAIR_FUNCTIONS = dict(
    laptop=laptop_repair,
    hp=hp_repair)

categories = list(REPAIR_FUNCTIONS.keys())

pars = ArgumentParser()
pars.add_argument('conf')
option = pars.parse_args(sys.argv[1:])

conf = ConfigParser()
conf.read(option.conf)

cf = dict(conf.items('main'))
repair_func = REPAIR_FUNCTIONS[cf['category']]

download_dirs = []
for url in cf['url'].strip().splitlines():
    print(url)
    p = urlparse(url)
    shop_path = p.path.lstrip('/').split('/')[0]
    web_name = p.netloc.split('.')[-2]
    download_dir = '-'.join([web_name, shop_path])
    download_dir = os.path.join(cf['base_download_dir'], download_dir)
    download_dirs.append((web_name, download_dir))
    print('  Download Directory:', download_dir)
    if os.path.exists(download_dir):
        if os.listdir(download_dir):
            print('  Ada isinya')
            continue
    else:
        os.mkdir(download_dir)
    a = Browser(url, download_dir)
    a.run()

csv_sources = []
for web_name, download_dir in download_dirs:
    output_file = os.path.split(download_dir)[-1] + '.csv'
    print(f'{download_dir} -> {output_file}')
    to_csv(web_name, download_dir, output_file)
    csv_sources.append(output_file)

for csv_source in csv_sources:
    name, ext = os.path.splitext(csv_source)
    output_file = [cf['category']] + name.split('-')[1:]
    output_file = '-'.join(output_file) + ext
    print(output_file)
    if 'gemini_url' in cf:
        gemini_parse(
            cf['category'], csv_source, output_file, cf['gemini_key'],
            cf['gemini_url'])
    else:
        d = dict(url=cf['ollama_url'], model=cf['ollama_model'])
        ai_info = dict(ollama=d)
        base_parse(cf['category'], csv_source, output_file, ai_info)
    repair_func(output_file)
    concat(cf['category'])
