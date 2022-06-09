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
    InvalidBrand,
    InvalidCategory,
    InvalidDescription,
    is_valid_range,
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
    url = Field()


class Crawler(Spider):
    name = 'laptop'
    parser_classes = dict()  # Override, please

    def __init__(
            self, product_url=None, hostname=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_url = product_url
        self.hostname = hostname
        self.is_store_url = True
        if product_url:
            # Untuk parsing produk tertentu. Digunakan selama development:
            # ~/env/bin/scrapy runspider laptop.py -O laptop.csv
            # -a product_url=https://...
            if product_url.find('file') == 0:
                self.is_store_url = False
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
                self.is_store_url = product_url.find('official') > -1 or \
                    product_url.find('category') > -1

    def set_hostname(self, tmp_dir):
        if not self.hostname:
            self.hostname = os.path.split(tmp_dir)[-1]

    def parse(self, response):  # Override
        if not self.is_store_url:
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
            self.logger.warning(f'Ini bukan laptop {response.url}')
            return
        except InvalidDescription:
            self.logger.warning(f'Deskripsi tidak dipahami {response.url}')
            return
        if not is_valid_range('price', d['price'], float(d['price'])):
            return
        brand = d['brand'].lower()
        if brand not in self.valid_brands:
            self.logger.warning('Brand {brand} tidak terdaftar')
            return
        d['brand'] = self.valid_brands[brand]
        d['url'] = p.get_url()
        i = Product()
        for key in d:
            i[key] = d[key]
        return i
