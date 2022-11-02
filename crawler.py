import os
from urllib.parse import urlparse
from scrapy import (
    Spider,
    Request,
    )
from scrapy.item import (
    Item,
    Field,
    )
from parser import (
    InvalidCategory,
    InvalidDescription,
    )


class Product(Item):
    brand = Field()
    title = Field()
    price = Field()
    processor = Field()
    graphic = Field()
    memory = Field()
    memory_gb = Field()
    storage = Field()
    storage_gb = Field()
    monitor = Field()
    monitor_inch = Field()
    weight = Field()
    weight_kg = Field()
    battery = Field()
    battery_mah = Field()
    usb = Field()
    usb_c = Field()
    nfc = Field()
    compass = Field()
    network_5g = Field()
    url = Field()


class Crawler(Spider):
    name = 'laptop'
    parser_classes = dict()  # Override, please

    def __init__(
            self, product_url=None, hostname=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_url = product_url
        self.hostname = hostname
        if product_url:
            # Untuk parsing produk tertentu. Digunakan selama development:
            # ~/env/bin/scrapy runspider laptop.py -O laptop.csv
            # -a product_url=https://...
            if product_url.find('file') == 0:
                filename = product_url[7:]  # Hapus file://
                if os.path.isdir(filename):
                    self.start_urls = [
                        f'file://{filename}/{x}' for x in os.listdir(filename)]
                    self.set_hostname(filename)
                else:
                    self.start_urls = [product_url]
                    tmp_dir = os.path.split(filename)[0]
                    self.set_hostname(tmp_dir)
            else:
                self.start_urls = [product_url]

    def set_hostname(self, tmp_dir):
        if not self.hostname:
            self.hostname = os.path.split(tmp_dir)[-1]

    def parse(self, response):  # Override
        cls = self.get_parser_class(response)
        p = cls(response)
        if response.url.find('file') == 0 or not p.is_product_list():
            yield self.parse_product(response)
        else:
            urls = self.get_product_urls(response)
            for url in urls:
                yield Request(url, callback=self.product_generator)
            if urls:
                yield self.next_page(response)

    def get_parser_class(self, response):
        if self.hostname:
            name = self.hostname
        else:
            p = urlparse(response.url)
            name = p.netloc
        return self.parser_classes[name]

    def get_product_urls(self, response) -> list:
        cls = self.get_parser_class(response)
        return cls.get_product_urls(response)

    def product_generator(self, response):
        yield self.parse_product(response)

    def next_page(self, response):
        cls = self.get_parser_class(response)
        url = cls.next_page_url(response)
        if url:
            return Request(url, callback=self.parse)

    def parse_product(self, response) -> dict:
        cls = self.get_parser_class(response)
        p = cls(response)
        try:
            d = p.parse()
        except InvalidCategory:
            c = ' / '.join(p.CATEGORIES)
            self.logger.warning(f'Ini bukan {c} {response.url}')
            return
        except InvalidDescription:
            self.logger.warning(f'Deskripsi tidak dipahami {response.url}')
            return
        if not p.is_valid_range('price', d['price'], float(d['price'])):
            return
        brand = d['brand'].lower()
        d['url'] = p.get_url()
        if brand not in p.VALID_BRANDS:
            self.logger.warning(
                f'Brand {brand} tidak terdaftar {d["url"]}')
            return
        i = Product()
        for key in d:
            i[key] = d[key]
        return i
