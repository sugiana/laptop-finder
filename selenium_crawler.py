import sys
import os
from time import sleep
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class App:
    options_class = Options

    def __init__(self, argv=sys.argv[1:]):
        opt = self.options_class()
        pars = self.arg_parser()
        self.option = pars.parse_args(argv)
        if self.option.browser_tidak_tampak:
            opt.add_argument("--headless")
        self.set_driver(opt)

    def set_driver(self, opt):
        driver_manager = ChromeDriverManager()
        service = Service(driver_manager.install())
        self.driver = webdriver.Chrome(service=service, options=opt)

    def arg_parser(self):
        pars = ArgumentParser()
        pars.add_argument('--tmp-dir', required=True)
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
