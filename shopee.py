from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from parser import Parser as BaseParser
from laptop_parser import Parser as BaseLaptop
from hp_parser import Parser as BaseHP


XPATH_PRODUCT = '//div[contains(@class,"shop-search-result-view")]//a'
XPATH_PAGE = '//div[@class="shopee-page-controller"]/button[@class="shopee-button-no-outline"]'


class Crawler:
    def __init__(self, driver):
        self.driver = driver
        self.page = 1
        self.first_url = None  # Override, please

    def get_product_urls(self):
        urls = []
        for xs in self.driver.find_elements(By.XPATH, XPATH_PRODUCT):
            url = xs.get_attribute('href')
            if url not in urls:
                urls.append(url)
        return urls

    def next_page_url(self):
        self.page += 1
        s_page = str(self.page)
        for xs in self.driver.find_elements(By.XPATH, XPATH_PAGE):
            print([xs.text])
            if xs.text == s_page:
                return f'{self.first_url}&page={self.page-1}'

    def UNUSED_click_next_page(self):
        try:
            xs = self.driver.find_element(By.XPATH, XPATH_NEXT)
            xs.click()
            return True
        except NoSuchElementException:
            return

    def is_product_list(self):
        return self.driver.page_source.lower().find(
                'shop-search-result-view') > -1

    def is_page_not_found(self):
        return self.driver.page_source.lower().find(
                'It looks like something is missing!') > -1


XPATH_TITLE = '//title/text()'
XPATH_PRICE = '//div[contains(@class,"items-center")]'\
              '/div[contains(@class,"items-center")]/div/div'
XPATH_URL = '//meta[@property="og:url"]/@content'


class Parser(BaseParser):
    def parse_desc(self):
        x = self.response.xpath(
                '//div[contains(@class,"product-detail")]/div/div')
        return x[3].xpath('div').extract()[0]

    XPATH_INFO = '//div[contains(@class,"product-detail")]/div/div/div'
    XPATH_DESC = parse_desc

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:  # Override
        s = self.response.xpath(XPATH_PRICE)[0].xpath('text()').extract()[0]
        return s.replace('Rp', '').replace('.', '')

    def get_url(self) -> str:  # Override
        return self.response.xpath(XPATH_URL).extract()[0]

    def get_brand(self) -> str:  # Override
        return self.info['Merek']


class Laptop(Parser, BaseLaptop):
    def get_info(self):  # Override
        r = Parser.get_info(self)
        if 'Tipe Laptop' in r:
            r['Kategori'] = 'Laptop'
        return r


class HP(Parser, BaseHP):
    def get_info(self):  # Override
        r = Parser.get_info(self)
        if 'Kapasitas Penyimpanan' in r:
            r['Kategori'] = 'Smartphone'
        return r
