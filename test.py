# -*- coding:utf-8 -*-

import os
import shutil
import unittest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from delver.crawler import Crawler
from delver.exceptions import CrawlerError
from delver.proxies import ProxyPool


class TestAll(unittest.TestCase):

    def setUp(self):
        self.urls = {
            'SIMPLE_HTML': 'https://httpbin.org/html',
            'SIMPLE_TABLE': 'https://www.w3schools.com/html/html_tables.asp',
            'USER_AGENT': 'https://httpbin.org/user-agent',
            'POST': 'https://httpbin.org/post',
            'COMPLEX_HTML': 'https://www.nytimes.com/',
            'FORM': 'https://httpbin.org/forms/post',
            'FORM2': 'https://eoryginalne.pl/kontakt',
            'GOOGLE': 'https://www.google.pl/',
            'LINKS': 'https://httpbin.org/links/10/0',
            'ROBOTS': 'https://httpbin.org/robots.txt',
            'IMAGE': 'https://httpbin.org/image/png',
            'FILE_UPLOAD': 'http://cgi-lib.berkeley.edu/ex/fup.html',
            'XML': 'https://httpbin.org/xml',
            'REDIRECT': 'https://httpbin.org/redirect/1',
            'REDIRECT_2_TIMES': 'https://httpbin.org/redirect/2',
            'COOKIES': 'https://httpbin.org/cookies',
            'BASIC_AUTH': 'https://httpbin.org/basic-auth/user/passwd',
            'GZIP': 'https://httpbin.org/gzip',
            'REST': 'https://jsonplaceholder.typicode.com/posts',
            'SCRAPING_QUOTES': 'http://quotes.toscrape.com/',
            'SCRAPING_BOOKSTORE': 'http://books.toscrape.com/',
            'GAZETA': 'http://www.gazeta.pl/0,0.html',
            'XKCD': 'https://xkcd.com/'
        }
        self.urls_list = [
            "https://www.nytimes.com/",
            "http://www.alexa.com/",
            "https://www.mozilla.org/en-US/",
            "https://www.amazon.com/",
            "https://www.walmart.com/",
            "http://www.biedronka.pl/pl",
            "https://pl.aliexpress.com/",
            "https://allegro.pl/",
            "https://httpbin.org/html",
            "https://github.com/"
        ]
        self.test_dir = os.path.join(os.getcwd(), 'test')
        self.upload_file = os.path.join(self.test_dir, 'upload.txt')
        os.makedirs(self.test_dir, exist_ok=True)

        with open(self.upload_file, 'wb') as f:
            f.write(b"If the road is easy, you're likely going the wrong way..")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_simple_http_page(self):
        c = Crawler()
        response = c.open(self.urls['SIMPLE_HTML'])
        self.assertEqual(response.status_code, 200)

    def test_find_title(self):
        c = Crawler()
        response = c.open(self.urls['SIMPLE_HTML'])
        self.assertEqual(response.status_code, 200)

    def test_find_links(self):
        c = Crawler()
        c.open(self.urls['GAZETA'])
        links = c.links(filters={
            'id': 'LinkArea:MT'
            }, match='EQUAL'
        )
        self.assertTrue(links)
        for href, attrs in links.items():
            self.assertEqual(attrs['id'], 'LinkArea:MT')

    def test_parse_form(self):
        c = Crawler()
        response = c.open(self.urls['FORM2'])
        self.assertEqual(response.status_code, 200)
        forms = c.forms(filters={'id': 'searchbox'})
        forms[0].fields = {
            'search_query': 'cute kittens'
        }
        self.assertEqual(forms[0].fields['search_query'].get('value'), 'cute kittens')

    def test_submit_form(self):
        c = Crawler()
        response = c.open(self.urls['FORM'])
        self.assertEqual(response.status_code, 200)
        forms = c.forms()
        forms[0].fields = {
            'custname': 'aaa',
            'delivery': '',
            'custemail': 'test@email.com',
            'comments': '',
            'size': 'medium',
            'topping': ['bacon', 'cheese'],
            'custtel': '+48606505888'
        }
        forms[0].submit(extra_values={'extra_value': "I am your father."})
        success = forms[0].check(
            phrase="I am your father.",
            url=self.urls['POST'],
            status_codes=[200])
        self.assertEqual(success, True)

    def test_response_history(self):
        c = Crawler()
        response = c.open(self.urls['REDIRECT_2_TIMES'])
        self.assertEqual(len(response.history), 2)

    def test_crawler_history(self):
        c = Crawler()
        c.open(self.urls['SIMPLE_HTML'])
        c.open(self.urls['LINKS'])
        history = c.history()
        self.assertEqual(history[0].url, self.urls['SIMPLE_HTML'])
        self.assertEqual(history[1].url, self.urls['LINKS'])

    def test_crawler_flow(self):
        c = Crawler()
        c.open(self.urls['SIMPLE_HTML'])
        c.open(self.urls['LINKS'])
        self.assertEqual(len(c.flow()), 2)

    def test_crawler_xpath(self):
        c = Crawler()
        c.open(self.urls['SIMPLE_HTML'])
        p_text = c.xpath('//p/text()')
        self.assertGreaterEqual(len(p_text), 1)

    def test_crawler_css(self):
        c = Crawler()
        c.open(self.urls['SIMPLE_HTML'])
        p_text = c.css('div')
        self.assertGreaterEqual(len(p_text), 1)

    def test_crawler_scraper_methods(self):
        c = Crawler()
        c.open(self.urls['SIMPLE_TABLE'])
        self.assertTrue(c.tables())
        self.assertTrue(c.title())
        self.assertTrue(c.images())

    def test_crawler_back_forward_navigation(self):
        c = Crawler(absolute_links=True)
        c.open(self.urls['SCRAPING_QUOTES'])
        tags_links = c.links(filters={'class': 'tag'})
        for link in tags_links.keys():
            c.follow(link)
        history = c.history()
        c.back()
        self.assertEqual(c.get_url(), history[-2].url)
        c.back()
        self.assertEqual(c.get_url(), history[-3].url)
        c.forward()
        self.assertEqual(c.get_url(), history[-2].url)
        self.assertRaises(CrawlerError, c.forward, step=5)

    def test_crawler_clear_flow(self):
        c = Crawler(absolute_links=True)
        c.open(self.urls['SCRAPING_QUOTES'])
        tags_links = c.links(filters={'class': 'tag'})
        for link in tags_links.keys():
            c.follow(link)
        self.assertTrue(c.history())
        c.clear()
        self.assertFalse(c.history())

    def test_crawler_cookies_handling(self):
        c = Crawler()
        c.open(self.urls['COMPLEX_HTML'])
        cookies_len = len(c.cookies)
        c.cookies['fake_cookie'] = 'dsf2r2dfsd32r32rrfsdfds'
        self.assertEqual(cookies_len+1, len(c.cookies))

    def test_crawler_useragent_set(self):
        c = Crawler()
        c.useragent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        json_response = c.open(self.urls['USER_AGENT']).json()
        self.assertEqual(c.useragent, json_response['user-agent'])

    def test_crawler_overridden_useragent(self):
        c = Crawler()
        c.useragent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        one_time_useragent = 'Godzilla'
        json_response = c.open(self.urls['USER_AGENT'], headers={'user-agent': one_time_useragent}).json()
        self.assertEqual(one_time_useragent, json_response['user-agent'])

    def test_download_file(self):
        c = Crawler()
        file_name = 'test.png'
        c.download(
            self.urls['USER_AGENT'],
            self.test_dir,
            name=file_name
        )
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, file_name)))

    def test_download_images_list(self):
        """ Download list of images in parallel.
        """
        c = Crawler()
        c.open(self.urls['XKCD'])
        full_images_urls = [c.join_url(src) for src in c.images()]
        downloaded_files = c.download_files(self.test_dir, files=full_images_urls)
        self.assertEqual(len(full_images_urls), len(downloaded_files))

    def test_form_file_upload(self):
        """Uploading a file through """
        c = Crawler()
        c.open(self.urls['FILE_UPLOAD'])
        forms = c.forms()
        forms[0].fields = {
            'note': 'Towel cat picture',
            'upfile': open(self.upload_file, 'r')
        }
        forms[0].submit()
        success = forms[0].check(
            phrase="road is easy",
            status_codes=[200])
        self.assertTrue(success)

    def test_proxy_pool(self):
        proxies = [
            "117.143.109.159:80",
            "117.143.109.163:80",
            "162.243.108.161:3128",
            "195.14.242.39:80",
            "202.57.129.228:8080",
            "212.124.171.144:80",
            "216.249.79.140:21320",
            "220.130.34.177:80"
            "52.10.247.166:80",
            "77.51.16.170:80",
        ]
        proxy_pool = ProxyPool()
        proxy_pool.load_proxies(proxies, test=True)
        working = proxy_pool.working()
        self.assertEqual(len(proxies), len(proxy_pool))

    def test_run_crawler_in_threads(self):
        c = Crawler()
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(c.open, self.urls_list)
        self.assertEqual(len(list(results)), 10)

    def test_run_crawler_in_processes(self):
        c = Crawler()
        with ProcessPoolExecutor(max_workers=4) as executor:
            results = executor.map(c.open, self.urls_list)
        self.assertEqual(len(list(results)), 10)

    def test_run_crawler_in_threads_download_images(self):

        def open_and_download(url):
            response = c.open(url)
            full_images_urls = [c.join_url(src) for src in c.images()]
            downloaded_files = c.download_files(self.test_dir, files=full_images_urls)
            self.assertEqual(len(full_images_urls), len(downloaded_files))
            return response

        c = Crawler()
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(open_and_download, self.urls_list)

        self.assertEqual(len(list(results)), 10)

    def test_crawler_custom_submit(self):
        c = Crawler()
        data = {
            'name': 'Luciano Ramalho',
            'title': 'Fluent Python'
        }
        c.submit(
            url=self.urls['POST'],
            data=data
        )
        result = c.response().json()
        self.assertEqual(result.get('form'), data)


if __name__ == '__main__':
    unittest.main()