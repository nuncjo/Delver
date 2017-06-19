# -*- coding:utf-8 -*-

import unittest

from delver.crawler import Crawler
from delver.exceptions import CrawlerError
from delver.proxies import ProxyPool


class TestAll(unittest.TestCase):

    def setUp(self):
        self.urls = {
            'SIMPLE_HTML': 'https://httpbin.org/html',
            'SIMPLE_TABLE': 'https://www.w3schools.com/html/html_tables.asp',
            'USER_AGENT': 'https://httpbin.org/user-agent',
            'COMPLEX_HTML': 'https://www.nytimes.com/',
            'FORM': 'https://httpbin.org/forms/post',
            'FORM2': 'https://eoryginalne.pl/kontakt',
            'GOOGLE': 'https://www.google.pl/',
            'LINKS': 'https://httpbin.org/links/10/0',
            'ROBOTS': 'https://httpbin.org/robots.txt',
            'XML': 'https://httpbin.org/xml',
            'REDIRECT': 'https://httpbin.org/redirect/1',
            'REDIRECT_2_TIMES': 'https://httpbin.org/redirect/2',
            'COOKIES': 'https://httpbin.org/cookies',
            'BASIC_AUTH': 'https://httpbin.org/basic-auth/user/passwd',
            'GZIP': 'https://httpbin.org/gzip',
            'REST': 'https://jsonplaceholder.typicode.com/posts',
            'SCRAPING_QUOTES': 'http://quotes.toscrape.com/',
            'SCRAPING_BOOKSTORE': 'http://books.toscrape.com/',
            'GAZETA': 'http://www.gazeta.pl/0,0.html'
        }

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
            url='https://httpbin.org/post',
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

    def test_crawler_proxy_set(self):
        pass

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

    def test_crawler_safe_mode(self):
        """Mode respecting robots.txt and timeouts before requests"""
        pass

    def test_crawler_post_back_reload_post(self):
        """Posting form, back and post again"""
        pass

    def test_form_file_upload(self):
        """Uploading a file through """
        pass

    def test_crawler_file_download(self):
        """Uploading a file through """
        pass

    def test_proxy_pool(self):
        proxies = [
            "110.136.228.250:80",
            "166.78.156.247:80",
            "173.234.216.40:21320",
            "178.45.192.153:80",
            "202.181.103.212:80",
            "216.150.41.16:8888",
            "31.193.223.87:80",
            "42.121.18.43:8080",
            "88.85.240.60:8080",
            "94.180.156.203:3128"
        ]
        proxy_pool = ProxyPool()
        proxy_pool.load_proxies(proxies, test=False)
        working = proxy_pool.working()
        self.assertEqual(len(proxies), len(proxy_pool))


if __name__ == '__main__':
    unittest.main()