import os
import unicodedata
import re
from time import sleep
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tokopedia import ListParser as TokopediaListParser
from macstore import ListParser as MacstoreListParser


# https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).\
                encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def nice_filename(url):
    s = urlparse(url).path.lstrip('/').replace('/', '.')
    s = slugify(s)
    return s + '.html'


class Browser:
    parser_classes = {
        'www.tokopedia.com': TokopediaListParser,
        'macstore.id': MacstoreListParser}

    def __init__(self, url, download_dir, is_ready_stock=True):
        self.url = url
        self.download_dir = download_dir
        self.is_ready_stock = is_ready_stock
        driver_manager = ChromeDriverManager()
        service = Service(driver_manager.install())
        opt = Options()
        self.driver = webdriver.Chrome(service=service, options=opt)

    def scroll(self, max_count=7, delay=2, height=200):
        x = 0
        while x < max_count:
            script = f'window.scrollTo(0, {height});'
            self.driver.execute_script(script)
            sleep(delay)
            x += 1
            height += height

    def save(self, url, full_path):
        while True:
            try:
                with open(full_path, 'w') as f:
                    f.write(self.driver.page_source)
                    print(f'File {full_path} tersimpan.')
                break
            except OSError as e:
                if e.errno != 36:
                    raise e
                # errno 36 arttinya nama file terlalu panjang, kurangi 1 huruf
                full_path, ext = os.path.splitext(full_path)
                full_path = full_path[:-1]
                full_path = full_path + ext

    def save_list(self, urls):
        for url in urls:
            filename = nice_filename(url)
            full_path = os.path.join(self.download_dir, filename)
            if os.path.exists(full_path):
                print(f'File {full_path} sudah ada.')
                continue
            self.driver.get(url)
            self.scroll(2)
            self.save(url, full_path)

    def run(self):
        p = urlparse(self.url)
        cls = self.parser_classes.get(p.netloc)
        if not cls:
            raise Exception(f'Parser untuk {p.netloc} belum tersedia')
        csv_file = self.download_dir + '.csv'
        product_urls = []
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            for index, values in df.iterrows():
                product_urls.append(values['url'])
        else:
            parser = cls(self.driver, self.is_ready_stock)
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
                else:
                    product_urls += [url]
                url = parser.next_page_url()
                if not url:
                    print('Tidak ada halaman berikutnya.')
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

    url = 'https://www.tokopedia.com/nvidiageforcelt/product'
    help_url = f'default {url}'

    marketplace = urlparse(url).netloc.split('.')[-2]
    shop_name = urlparse(url).path.split('/')[1]
    download_dir = f'/home/sugiana/tmp/{marketplace}-{shop_name}'
    help_dir = f'default {download_dir}'

    stock_choices = ['ready', 'all']
    stock = stock_choices[0]
    help_stock = f'Apakah unduh semua stok ? default: {stock}. '\
                 'all berarti yang habis pun diunduh.'

    pars = ArgumentParser()
    pars.add_argument('--url', default=url, help=help_url)
    pars.add_argument('--download-dir', default=download_dir, help=help_dir)
    pars.add_argument(
        '--stock', choices=stock_choices, default=stock, help=help_stock)
    option = pars.parse_args(sys.argv[1:])

    is_ready_stock = option.stock == 'ready'
    a = Browser(option.url, option.download_dir, is_ready_stock)
    a.run()
