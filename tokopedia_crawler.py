from time import sleep
from selenium.webdriver.common.by import By
from selenium_crawler import App as Base


XPATH_PRODUCT = '//div[contains(@data-testid,"divProductWrapper")]//a'
START_URL = 'https://www.tokopedia.com/nvidiageforcelt/product'
EMPTY_MSG = 'toko ini belum memiliki produk'


class App(Base):
    def run(self):  # Override
        page_url = START_URL
        page = 1
        while True:
            self.driver.get(page_url)
            self.scroll()
            if self.driver.page_source.lower().find(EMPTY_MSG) > -1:
                break
            product_urls = []
            for xs in self.driver.find_elements(By.XPATH, XPATH_PRODUCT):
                product_url = xs.get_attribute('href')
                if product_url in product_urls:
                    continue
                product_urls.append(product_url)
            no = 0
            for product_url in product_urls:
                no += 1
                self.driver.get(product_url)
                self.scroll(1)
                filename = f'page-{page:02}-product-{no:03}.html'
                self.save(filename)
            page += 1
            page_url = f'{START_URL}/page/{page}'
        self.driver.quit()


if __name__ == '__main__':
    a = App()
    a.run()
