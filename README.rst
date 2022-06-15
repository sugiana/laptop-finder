Laptop Finder
=============

`Streamlit <https://streamlit.io>`_ application for laptop finder. Usage::

    $ python3 -m venv ~/env
    $ ~/env/bin/pip install --upgrade pip wheel
    $ ~/env/bin/pip install -r requirements.txt
    $ ~/env/bin/streamlit run laptop_finder.py

For HP finder::

    $ ~/env/bin/streamlit run hp_finder.py


Crawler
-------

Crawl and parse using Scrapy::

    $ ~/env/bin/scrapy runspider laptop_crawler.py -O laptop.csv
    $ ~/env/bin/scrapy runspider hp_crawler.py -O hp.csv

Crawl using Selenium (need desktop environment)::

    $ ~/env/bin/python selenium_laptop_crawler.py --tmp-dir=/tmp
    $ ~/env/bin/python selenium_hp_crawler.py --tmp-dir=/tmp

Parse using Scrapy::

    $ ~/env/bin/scrapy runspider laptop_crawler.py -a product_url=file:///tmp/laptop/www.tokopedia.com -O laptop-www.tokopedia.com.csv
    $ ~/env/bin/scrapy runspider hp_crawler.py -a product_url=file:///tmp/hp/www.tokopedia.com -O hp-www.tokopedia.com.csv

Merge all CSV files::

    $ ~/env/bin/python csv_concat.py laptop
    $ ~/env/bin/python csv_concat.py hp 

Press Ctrl-C to stop ``streamlit`` and run again::

    $ ~/env/bin/streamlit run laptop_finder.py

Good luck.
