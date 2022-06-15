import sys
import os
from time import sleep
from argparse import ArgumentParser
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


tmp_dir = '/tmp'
help_tmp = f'default {tmp_dir}'


def nice_filename(url):
    return urlparse(url).path.lstrip('/').replace('/', '.') + '.html'


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


class App:
    options_class = Options
    start_urls = []
    parser_classes = dict()

    def __init__(self, argv=sys.argv[1:]):
        opt = self.options_class()
        pars = self.arg_parser()
        self.option = pars.parse_args(argv)
        if self.option.browser_tidak_tampak:
            opt.add_argument("--headless")
        self.set_driver(opt)
        self.category_dir = os.path.join(self.option.tmp_dir, self.category)
        mkdir(self.category_dir)

    def set_driver(self, opt):
        driver_manager = ChromeDriverManager()
        service = Service(driver_manager.install())
        self.driver = webdriver.Chrome(service=service, options=opt)

    def arg_parser(self):
        pars = ArgumentParser()
        pars.add_argument('--start-url')
        pars.add_argument('--tmp-dir', default=tmp_dir, help=help_tmp)
        pars.add_argument('--browser-tidak-tampak', action='store_true')
        return pars

    def scroll(self, max_count=7, delay=2, height=200):
        x = 0
        while x < max_count:
            script = f'window.scrollTo(0, {height});'
            self.driver.execute_script(script)
            sleep(delay)
            x += 1
            height += height

    def save(self, filename):
        full_path = os.path.join(self.option.tmp_dir, filename)
        with open(full_path, 'w') as f:
            f.write(self.driver.page_source)
            print(f'File {full_path} tersimpan.')

    def get_parser_class(self, url):
        p = urlparse(url)
        return self.parser_classes[p.netloc]

    def run(self):
        if self.option.start_url:
            url_list = [self.option.start_url]
        else:
            url_list = self.start_urls
        for url in url_list:
            p = urlparse(url)
            tmp_dir = os.path.join(self.category_dir, p.netloc)
            mkdir(tmp_dir)
            cls = self.get_parser_class(url)
            p = cls(self.driver)
            page = 1
            while True:
                self.driver.get(url)
                self.scroll()
                if p.is_page_not_found():
                    break
                is_list = p.is_product_list()
                if is_list:
                    product_urls = p.get_product_urls()
                else:
                    product_urls = [url]
                no = 0
                for product_url in product_urls:
                    no += 1
                    self.driver.get(product_url)
                    self.scroll(2)
                    filename = nice_filename(product_url)
                    filename = os.path.join(tmp_dir, filename)
                    self.save(filename)
                if is_list:
                    break
                page += 1
                page_url = f'{self.option.start_url}/page/{page}'
        self.driver.quit()
