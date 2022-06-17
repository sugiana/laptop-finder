from urllib.parse import urlparse
from laptop_parser import Parser as BaseLaptop
from hp_parser import Parser as BaseHP


XPATH_TITLE = '//h1/text()'
XPATH_PRODUCT = '//div[contains(@class,"o-layout--responsive")]/div'
XPATH_PRICE_DISC = '//div[contains(@class,"c-product-price -discounted")]'\
                   '/span/text()'
XPATH_PRICE_ORIG = '//div[contains(@class,"c-product-price -original")]'\
                   '/span/text()'


class Base:
    XPATH_INFO = '//table[@class="c-information__table"]/tbody/tr'
    XPATH_DESC = '//div[@class="c-information__description-txt"]'

    @classmethod
    def get_product_urls(cls, response) -> list:  # Override
        r = []
        for xs in response.xpath(XPATH_PRODUCT):
            url = xs.xpath('div/div')[0]
            url = url.xpath('a/@href').extract()
            if not url:
                return r
            url = url[0]
            r.append(url)
        return r

    @classmethod
    def next_page_url(cls, response) -> str:  # Override
        p = urlparse(response.url)
        if p.query:
            t = p.query.split('=')
            page = int(t[1])
        else:
            page = 1
        page += 1
        return f'{p.scheme}://{p.netloc}{p.path}?page={page}'

    def is_product_list(self):
        s = self.response.body.lower()
        return s.find(b'barang etalase') > -1 or \
            s.find(b'<strong>semua barang') > -1

    def get_info(self) -> dict:
        return super().get_info(3)

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:  # Override
        xs = self.response.xpath(XPATH_PRICE_DISC)
        if not xs:
            xs = self.response.xpath(XPATH_PRICE_ORIG)
        v = xs.extract()[0]
        return v.lstrip('Rp').replace('.', '')


class Laptop(Base, BaseLaptop):
    pass


class HP(Base, BaseHP):
    pass
