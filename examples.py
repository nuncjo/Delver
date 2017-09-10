# -*- coding:utf-8 -*-

from pprint import pprint
from delver import Crawler


def scraping_steam_specials():
    c = Crawler()
    c.logging = True
    c.useragent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    c.random_timeout = (0, 5)
    c.open('http://store.steampowered.com/search/?specials=1')
    titles, discounts, final_prices = [], [], []
    while c.links(filters={
        'class': 'pagebtn',
        'text': '>'
    }):
        c.open(c.current_results[0])
        titles.extend(
            c.xpath("//div/span[@class='title']/text()")
        )
        discounts.extend(
            c.xpath("//div[contains(@class, 'search_discount')]/span/text()")
        )
        final_prices.extend(
            c.xpath("//div[contains(@class, 'discounted')]//text()[2]").strip()
        )

    all_results = {
        row[0]: {
            'discount': row[1],
            'final_price': row[2]
        } for row in zip(titles, discounts, final_prices)}
    pprint(all_results)


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
