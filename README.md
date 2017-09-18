Delver
========================

Programmatic web browser/crawler in Python. **Alternative to Mechanize, RoboBrowser, MechanicalSoup**
and others. Strict power of Request and Lxml. Some features and methods usefull in scraping "out of the box".

- [Basic examples](#basic-examples)
    - [Form submit](#form-submit)
    - [Find links narrowed by filters](#find-links-narrowed-by-filters)
    - [Download file](#download-file)
    - [Download files list in parallel](#download-files-list-in-parallel)
    - [Xpath selectors](#xpath-selectors)
    - [Css selectors](#css-selectors)
    - [Xpath result with filters](#xpath-result-with-filters)
- [Use examples](#use-examples)
    - [Scraping Steam Specials using XPath](#scraping-steam-specials-using-xpath)
    - [Simple tables scraping out of the box](#simple-tables-scraping-out-of-the-box)
    - [User login](#user-login)
    - [One Punch Man Downloader](#one-punch-man-downloader)

- - -

## Basic examples


## Form submit

```python

        >>> from delver import Crawler
        >>> c = Crawler()
        >>> response = c.open('https://httpbin.org/forms/post')
        >>> forms = c.forms()

        # Filling up fields values:
        >>> form = forms[0]
        >>> form.fields = {
        ...    'custname': 'Ruben Rybnik',
        ...    'custemail': 'ruben.rybnik@fakemail.com',
        ...    'size': 'medium',
        ...    'topping': ['bacon', 'cheese'],
        ...    'custtel': '+48606505888'
        ... }
        >>> submit_result = c.submit(form)
        >>> submit_result.status_code
        200

        # Checking if form post ended with success:
        >>> c.submit_check(
        ...    form,
        ...    phrase="Ruben Rybnik",
        ...    url='https://httpbin.org/forms/post',
        ...    status_codes=[200]
        ... )
        True
```

## Find links narrowed by filters

```python

        >>> c = Crawler()
        >>> c.open('https://httpbin.org/links/10/0')
        <Response [200]>

        # Links can be filtered by some html tags and filters
        # like: id, text, title and class:
        >>> links = c.links(
        ...     tags = ('style', 'link', 'script', 'a'),
        ...     filters = {
        ...         'text': '7'
        ...     },
        ...     match='NOT_EQUAL'
        ... )
        >>> len(links)
        8
```

## Download file

```python

        >>> import os

        >>> c = Crawler()
        >>> local_file_path = c.download(
        ...     local_path='test',
        ...     url='https://httpbin.org/image/png',
        ...     name='test.png'
        ... )
        >>> os.path.isfile(local_file_path)
        True
```

## Download files list in parallel

```python

        >>> c = Crawler()
        >>> c.open('https://xkcd.com/')
        <Response [200]>
        >>> full_images_urls = [c.join_url(src) for src in c.images()]
        >>> downloaded_files = c.download_files('test', files=full_images_urls)
        >>> len(full_images_urls) == len(downloaded_files)
        True
```

## Xpath selectors

```python

        c = Crawler()
        c.open('https://httpbin.org/html')
        p_text = c.xpath('//p/text()')
```

## Css selectors

```python

        c = Crawler()
        c.open('https://httpbin.org/html')
        p_text = c.css('div')
```

## Xpath result with filters

```python

        c = Crawler()
        c.open('https://www.w3schools.com/')
        filtered_results = c.xpath('//p').filter(filters={'class': 'w3-xlarge'})
```

## Using retries

```python

        c = Crawler()
        # sets max_retries to 2 means that after there will be max two attempts to open url
        # if first attempt will fail, wait 1 second and try again, second attempt wait 2 seconds
        # and then try again
        c.max_retries = 2
        c.open('http://www.delver.cg/404')
```

## Use examples


## Scraping Steam Specials using XPath

```python

    from pprint import pprint
    from delver import Crawler

    c = Crawler(absolute_links=True)
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
```

## Simple tables scraping out of the box

```python

    from pprint import pprint
    from delver import Crawler

    c = Crawler(absolute_links=True)
    c.logging = True
    c.useragent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    c.open("http://www.boxofficemojo.com/daily/")
    pprint(c.tables())
```

## User login

```python


    from delver import Crawler

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
```

## One Punch Man Downloader

```python

    import os
    from delver import Crawler

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


    downloader = OnePunchManDownloader()
    downloader.run()
```
