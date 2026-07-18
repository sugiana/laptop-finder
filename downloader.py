import os
import re
import json
from time import sleep
from urllib.parse import urlparse
import requests
from unittest.mock import patch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tools import nice_filename
import tokopedia
import macstore


# Simpan fungsi asli agar tidak terjadi rekursi tak terbatas
original_request = requests.Session.request


def patched_request(self, method, url, **kwargs):
    kwargs.setdefault('timeout', 120)
    return original_request(self, method, url, **kwargs)


class Browser:
    parser_classes = {
        'www.tokopedia.com': tokopedia,
        'macstore.id': macstore}

    def __init__(self, url, download_dir, is_ready_stock=True):
        self.url = url
        self.download_dir = download_dir
        self.is_ready_stock = is_ready_stock
        driver_manager = ChromeDriverManager()
        with patch('requests.Session.request', patched_request):
            installer = driver_manager.install()
        service = Service(installer)
        opt = Options()
        opt.add_argument('--disable-gpu')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=service, options=opt)

    def scroll(self, max_count=7, delay=2, height=200):
        x = 0
        while x < max_count:
            script = f'window.scrollTo(0, {height});'
            self.driver.execute_script(script)
            sleep(delay)
            x += 1
            height += height

    def save(self, url: str, full_path: str, html='', variant={}):
        if not html:
            html = self.driver.page_source
        d = dict(url=url)
        if variant:
            d['variant'] = variant
        json_str = json.dumps(d)
        name, ext = os.path.splitext(full_path)
        json_file = name + '.json'
        while True:
            try:
                with open(json_file, 'w') as f:
                    f.write(json_str)
                print(f'File {json_file} tersimpan.')
                break
            except OSError as e:
                if e.errno != 36:
                    raise e
                # errno 36 arttinya nama file terlalu panjang, kurangi 1 huruf
                json_file, ext = os.path.splitext(json_file)
                json_file = json_file[:-1]
                json_file = json_file + ext
        name, ext = os.path.splitext(json_file)
        html_file = name + '.html'
        with open(html_file, 'w') as f:
            f.write(html)
        print(f'File {html_file} tersimpan.')

    def get_full_path(self, url):
        filename = nice_filename(url)
        return os.path.join(self.download_dir, filename)

    def save_list(self, urls: list):
        parser = self.module.ListParser(self.driver, self.is_ready_stock)
        for url in urls:
            full_path = self.get_full_path(url)
            if os.path.exists(full_path):
                print(f'File {full_path} sudah ada.')
                continue
            self.driver.get(url)
            self.scroll(2)
            if parser.has_variant():
                variants = parser.get_variants()
                for variant, variant_url, html in variants:
                    full_path = self.get_full_path(variant_url)
                    if os.path.exists(full_path):
                        print(f'File {full_path} sudah ada.')
                        continue
                    self.save(variant_url, full_path, html, variant)
            else:
                self.save(url, full_path)

    def run(self):
        p = urlparse(self.url)
        self.module = self.parser_classes.get(p.netloc)
        if not self.module:
            raise Exception(f'Parser untuk {p.netloc} belum tersedia')
        csv_file = self.download_dir + '.csv'
        product_urls = []
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            for index, values in df.iterrows():
                product_urls.append(values['url'])
        else:
            parser = self.module.ListParser(self.driver, self.is_ready_stock)
            page_urls = []
            url = self.url
            while True:
                if url in page_urls:
                    print(f'{url} terulang.')
                    break
                print(f'Product list {url}')
                self.driver.get(url)
                self.scroll()
                if parser.is_page_not_found():
                    print(f'{url} tidak ada.')
                    break
                if parser.is_product_list():
                    page_urls.append(url)
                    product_urls += parser.get_product_urls()
                    url = parser.next_page_url()
                    if not url:
                        print('Tidak ada halaman berikutnya.')
                        break
                else:
                    product_urls += [url]
                    break
            if product_urls:
                data = dict(url=product_urls)
                df = pd.DataFrame(data)
                df.to_csv(csv_file, index=False)
                print('Daftar URL produk sudah disimpan di', csv_file)
        self.save_list(product_urls)
        self.driver.quit()


if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    from urllib.parse import urlparse

    url = 'https://www.tokopedia.com/nvidiageforcelt/product'
    help_url = f'default {url}'

    stock_choices = ['ready', 'all']
    stock = stock_choices[0]
    help_stock = (
        f'Apakah unduh semua stok ? default: {stock}. '
        'all berarti yang habis pun diunduh.')

    pars = ArgumentParser()
    pars.add_argument('--url', default=url, help=help_url)
    pars.add_argument('--download-dir')
    pars.add_argument(
        '--stock', choices=stock_choices, default=stock, help=help_stock)
    option = pars.parse_args(sys.argv[1:])

    if option.download_dir:
        download_dir = option.download_dir
    else:
        home_dir = os.path.expanduser('~')
        base_download_dir = os.path.join(home_dir, 'tmp')
        if not os.path.exists(base_download_dir):
            print('Create', base_download_dir)
            os.mkdir(base_download_dir)
        p = urlparse(url)
        web_path = p.path.lstrip('/').replace('/', '-')
        web_name = p.netloc.split('.')[-2]
        download_dir = '-'.join([web_name, web_path])
        download_dir = os.path.join(base_download_dir, download_dir)

    is_ready_stock = option.stock == 'ready'
    a = Browser(option.url, download_dir, is_ready_stock)
    a.run()
