from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from parsel import Selector
from parser import (
    HTML2Text,
    BaseListParser,
    BaseProductParser,
    UrlNotFound,
    DescriptionNotFound
    )


XPATH_LIST = '//div[contains(@data-testid,"divProductWrapper")]//a'
XPATH_NEXT = '//a[@data-testid="btnShopProductPageNext"]'


class ListParser(BaseListParser):
    def get_product_urls(self):
        self.is_stock = True
        urls = []
        self.is_stock = True
        for xs in self.driver.find_elements(By.XPATH, XPATH_LIST):
            # Apakah hanya membaca produk yang ada stoknya ?
            if self.is_ready_stock:
                html = xs.get_attribute('innerHTML')
                if html.find('divImgProductOverlay') > -1:
                    # Nanti dibaca next_page_urls(). Jika ketemu produk yang
                    # tidak ada stoknya maka jangan dilanjutkan karena
                    # produk-produk berikutnya pasti juga sudah habis.
                    self.is_stock = False
                    return urls
            url = xs.get_attribute('href')
            if url not in urls:
                urls.append(url)
        return urls

    def next_page_url(self):
        if not self.is_stock:
            return
        try:
            xs = self.driver.find_element(By.XPATH, XPATH_NEXT)
            return xs.get_attribute('href')
        except NoSuchElementException:
            return

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
XPATH_INFO = '//ul[@data-testid="lblPDPInfoProduk"]/li'
XPATH_DESC = '//div[@data-testid="lblPDPDescriptionProduk"]'
XPATH_STOCK = '//p[@data-testid="stock-label"]'

EVERY_LINE = 2


class ProductParser(BaseProductParser):
    def __init__(self, html):
        super().__init__(html)
        url = self.get_url()
        if not url:
            raise UrlNotFound()
        info = self.get_info()
        is_new = info['Kondisi'] == 'Baru' and 1 or 0
        self.data = dict(
            url=url,
            shop_name=self.get_shop_name(),
            title=self.get_title(),
            price=self.get_price(),
            info=info,
            is_new=is_new,
            stock=self.get_stock(),
            description=self.get_description())

    def get_url(self) -> str:
        r = self.sel.xpath(XPATH_URL).extract()
        return r and r[0]

    def get_shop_name(self) -> str:
        r = self.sel.xpath(XPATH_SHOP_NAME).extract()
        return r and r[0] or None

    def get_title(self) -> str:
        return self.sel.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:
        s = self.sel.xpath(XPATH_PRICE).extract()[0].lstrip('Rp')
        s = s.replace('.', '')
        return float(s)

    def get_info(self) -> dict:
        lines = []
        for xs in self.sel.xpath(XPATH_INFO):
            s = xs.extract()
            p = HTML2Text()
            p.feed(s)
            lines += p.lines
        numbers = range(0, len(lines), EVERY_LINE)
        lines = [lines[x:x+EVERY_LINE] for x in numbers]
        d = dict()
        for t in lines:
            key = t[0]
            val = t[-1]
            key = key.split(':')[0]
            d[key] = val
        return d

    def get_description(self) -> str:
        xs = self.sel.xpath(XPATH_DESC)
        s = xs.extract()
        if not s:
            raise DescriptionNotFound()
        s = s[0]
        p = HTML2Text()
        p.feed(s)
        return '\n'.join(p.lines)

    def get_stock(self) -> int:
        xs = self.sel.xpath(XPATH_STOCK)
        s = xs.extract()
        if not s:
            return 1
        s = s[0]
        p = HTML2Text()
        p.feed(s)
        if p.lines[-1].lower().find('tidak') > -1:
            return 0
        s = p.lines[-1].split()[-1]
        s = s == 'Habis' and '0' or s.replace('.', '')
        try:
            return int(s)
        except ValueError:
            return 1
