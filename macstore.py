# https://macstore.id/product-category/macbook/
import json
from parsel import Selector
from parser import (
    HTML2Text,
    BaseProductParser,
    )


XPATH_PRODUCT = '//a[contains(@class,"woocommerce-LoopProduct-link")]/@href'


class ListParser:
    def __init__(self, driver):
        self.driver = driver

    def get_product_urls(self):
        sel = Selector(self.driver.page_source)
        return [str(x) for x in sel.xpath(XPATH_PRODUCT)]

    def next_page_url(self):
        pass

    def is_product_list(self):
        return self.driver.page_source.lower().find('showing all') > -1

    def is_page_not_found(self):
        pass


XPATH_URL = '//script[@type="application/ld+json"]/text()'
XPATH_TITLE = '//h1/text()'
XPATH_PRICE = '//p[@class="price"]/ins/span[contains('\
              '@class,"woocommerce-Price-amount")]/bdi/text()'
XPATH_DESC = '//div[@class='\
             '"woocommerce-product-details__short-description"]'


class ProductParser(BaseProductParser):
    def __init__(self, html):
        super().__init__(html)
        self.data.update(dict(
            url=self.get_url(),
            shop_name='Macstore',
            brand='Apple',
            title=self.get_title(),
            price=self.get_price(),
            description=self.get_description()))

    def get_url(self) -> str:
        row = self.sel.xpath(XPATH_URL)[0]
        d = json.loads(str(row))
        d = d['@graph'][1]
        return d['url']

    def get_title(self) -> str:
        return self.sel.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> float:
        s = self.sel.xpath(XPATH_PRICE).extract()[0].lstrip()
        s = s.replace('.', '').replace(',', '.')
        return float(s)

    def get_description(self) -> str:
        xs = self.sel.xpath(XPATH_DESC)
        s = xs.extract()[0]
        p = HTML2Text()
        p.feed(s)
        return '\n'.join(p.lines)
