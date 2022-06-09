from parser import Parser


XPATH_TITLE = '//h1/text()'
XPATH_PRICE = '//div[@class="price"]/text()'
XPATH_URL = '//meta[contains(@name,"desktop_url")]/@content'


class Laptop(Parser):
    XPATH_INFO = '//ul[@data-testid="lblPDPInfoProduk"]/li'
    XPATH_DESC = '//div[@data-testid="lblPDPDescriptionProduk"]'

    def get_title(self) -> str:  # Override
        return self.response.xpath(XPATH_TITLE).extract()[0]

    def get_price(self) -> str:  # Override
        s = self.response.xpath(XPATH_PRICE).extract()[0].lstrip('Rp')
        return s.replace('.', '')

    def get_url(self) -> str:  # Override
        return self.response.xpath(XPATH_URL).extract()[0]
