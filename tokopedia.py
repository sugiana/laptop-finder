from selenium.webdriver.common.by import By
from parser import Parser as BaseParser
from laptop_parser import Parser as BaseLaptop
from hp_parser import Parser as BaseHP


XPATH_PRODUCT = '//div[contains(@data-testid,"divProductWrapper")]//a'


class Crawler:
    def __init__(self, driver):
        self.driver = driver

    def get_product_urls(self):
        urls = []
        for xs in self.driver.find_elements(By.XPATH, XPATH_PRODUCT):
            url = xs.get_attribute('href')
            if url not in urls:
                urls.append(url)
        return urls

    def is_product_list(self):
        return self.driver.page_source.lower().find(
                'jumlah produk per halaman') > -1

    def is_page_not_found(self):
        return self.driver.page_source.lower().find(
                'toko ini belum memiliki produk') > -1


XPATH_TITLE = '//h1/text()'
XPATH_PRICE = '//div[@class="price"]/text()'
XPATH_URL = '//meta[contains(@name,"desktop_url")]/@content'
XPATH_SHOP_NAME = '//a[@data-testid="llbPDPFooterShopName"]/h2/text()'


class Parser(BaseParser):
    XPATH_INFO = '//ul[@data-testid="lblPDPInfoProduk"]/li'
    XPATH_DESC = '//div[@data-testid="lblPDPDescriptionProduk"]'

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:  # Override
        s = self.response.xpath(XPATH_PRICE).extract()[0].lstrip('Rp')
        return s.replace('.', '')

    def get_url(self) -> str:  # Override
        return self.response.xpath(XPATH_URL).extract()[0]

    def get_shop_name(self) -> str:
        return self.response.xpath(XPATH_SHOP_NAME).extract()[0]

    def get_brand(self) -> str:  # Override
        brand = super().get_brand()
        b_lower = brand.lower()
        if b_lower in self.VALID_BRANDS:
            return brand
        shop_name = self.get_shop_name()
        b_lower = shop_name.lower().split()[0]
        if b_lower in self.VALID_BRANDS:
            return self.VALID_BRANDS[b_lower]
        return brand


class Laptop(Parser, BaseLaptop):
    pass


class HP(Parser, BaseHP):
    pass
