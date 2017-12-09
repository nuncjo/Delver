# -*- coding:utf-8 -*-

import os

import psycopg2

from pprint import pprint
from delver import Crawler


def scraping_movies_table():
    c = Crawler()
    c.logging = True
    c.useragent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    c.open("http://www.boxofficemojo.com/daily/")
    pprint(c.tables())


def user_login():
    c = Crawler()
    c.useragent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/60.0.3112.90 Safari/537.36"
    )
    c.random_timeout = (0, 5)
    c.open('http://testing-ground.scraping.pro/login')
    forms = c.forms()
    if forms:
        login_form = forms[0]
        login_form.fields = {
            'usr': 'admin',
            'pwd': '12345'
        }
        c.submit(login_form)
        success_check = c.submit_check(
            login_form,
            phrase='WELCOME :)',
            status_codes=[200]
        )
        print(success_check)


class OnePunchManDownloader:
    """Downloads One Punch Man free manga chapers to local directories.
    Uses one main thread for scraper with random timeout.
    Uses 20 threads just for image downloads.
    """
    def __init__(self):
        self._target_directory = 'one_punch_man'
        self._start_url = "http://m.mangafox.me/manga/onepunch_man_one/"
        self.crawler = Crawler()
        self.crawler.random_timeout = (0, 5)
        self.crawler.useragent = "Googlebot-Image/1.0"

    def run(self):
        self.crawler.open(self._start_url)
        for link in self.crawler.links(filters={'text': 'Ch '}, match='IN'):
            self.download_images(link)

    def download_images(self, link):
        target_path = '{}/{}'.format(self._target_directory, link.split('/')[-2])
        full_chapter_url = link.replace('/manga/', '/roll_manga/')
        self.crawler.open(full_chapter_url)
        images = self.crawler.xpath("//img[@class='reader-page']/@data-original")
        os.makedirs(target_path, exist_ok=True)
        self.crawler.download_files(target_path, files=images, workers=20)


def one_punch_downloader():
    downloader = OnePunchManDownloader()
    downloader.run()


class WithConnection:

    def __init__(self, params):
        self._connection = psycopg2.connect(**params)
        self._connection.autocommit = True
        self._cursor = self._connection.cursor()

    def table_exists(self, table_name):
        self._cursor.execute('''
            select exists(
                select * from information_schema.tables where table_name='{}'
            )
        '''.format(table_name))
        return self._cursor.fetchone()[0]


def scrape_page(crawler):
    """ Scrapes rows from tables with promotions.

    :param crawler: <delver.crawler.Crawler object>
    :return: generator with page of rows
    """
    titles = crawler.xpath("//div/span[@class='title']/text()")
    discounts = crawler.xpath("//div[contains(@class, 'search_discount')]/span/text()")
    final_prices = crawler.xpath("//div[contains(@class, 'discounted')]//text()[2]").strip()
    yield [{
               'title': row[0],
               'discount': row[1],
               'price': row[2]
           } for row in zip(titles, discounts, final_prices)]


class SteamPromotionsScraper:
    """ Scraper which can be iterated through

    Usage example::
        >>> promotions_scraper = SteamPromotionsScraper()
        >>> for page in promotions_scraper:
        ...     pprint(page)

    """
    def __init__(self):
        self.crawler = Crawler()
        self.crawler.logging = True
        self.crawler.useragent = \
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        self.crawler.random_timeout = (0, 5)

    def scrape_by_page(self):
        self.crawler.open('http://store.steampowered.com/search/?specials=1')
        yield from scrape_page(self.crawler)
        while self.crawler.links(filters={
            'class': 'pagebtn',
            'text': '>'
        }):
            self.crawler.open(self.crawler.current_results[0])
            yield from scrape_page(self.crawler)

    def __iter__(self):
        return self.scrape_by_page()


class SteamPromotionsScraperDB(WithConnection):
    """Example with saving data to postgresql database

    Usage example::
        >>> promotions_scraper_db = SteamPromotionsScraperDB({
        ...     'dbname': "test",
        ...     'user': "testuser",
        ...     'password': "test"
        ... })
        >>> promotions_scraper.save_to_db()
    """

    def __init__(self, params):
        super().__init__(params)
        self.crawler = Crawler()
        self.crawler.logging = True
        self.crawler.useragent = \
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        self.crawler.random_timeout = (0, 5)

    def scrape_by_page(self):
        self.crawler.open('http://store.steampowered.com/search/?specials=1')
        yield from scrape_page(self.crawler)
        while self.crawler.links(filters={
            'class': 'pagebtn',
            'text': '>'
        }):
            self.crawler.open(self.crawler.current_results[0])
            yield from scrape_page(self.crawler)

    def save_to_db(self):
        if not self.table_exists('promotions'):
            self._cursor.execute(
                '''
                    CREATE TABLE promotions (
                        id serial PRIMARY KEY,
                        title varchar(255),
                        discount varchar(4),
                        price varchar(10)
                    );
                '''
            )
        for page in self.scrape_by_page():
            for row in page:
                self._cursor.execute(
                    '''
                        INSERT INTO promotions(title, discount, price)
                        VALUES(%s, %s, %s)
                    ''',
                    (row.get('title'), row.get('discount'), row.get('price'))
                )
                pprint(row)
