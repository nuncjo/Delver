Delver
========================

Programmatic web browser/crawler in Python. Alternative to Machanize, RoboBrowser, MechanicalSoup
and others. Strict power of Request and Lxml. Some features and methods usefull in scraping "out of the box".


.. code-block:: bash

    $ pip install delver

Example form submit:
----------------

.. code-block:: python

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


Find links narrowed by filters:
----------------

.. code-block:: python

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


Download file:
----------------

.. code-block:: python

        >>> import os

        >>> c = Crawler()
        >>> local_file_path = c.download(
        ...     local_path='test',
        ...     url='https://httpbin.org/image/png',
        ...     name='test.png'
        ... )
        >>> os.path.isfile(local_file_path)
        True


Download files list in parallel:
----------------

.. code-block:: python

        >>> c = Crawler()
        >>> c.open('https://xkcd.com/')
        <Response [200]>
        >>> full_images_urls = [c.join_url(src) for src in c.images()]
        >>> downloaded_files = c.download_files('test', files=full_images_urls)
        >>> len(full_images_urls) == len(downloaded_files)
        True


Using xpath selectors:
----------------

.. code-block:: python

        c = Crawler()
        c.open('https://httpbin.org/html')
        p_text = c.xpath('//p/text()')


Using css selectors:
----------------

.. code-block:: python

        c = Crawler()
        c.open('https://httpbin.org/html')
        p_text = c.css('div')


Using xpath result with filters:
----------------

.. code-block:: python

        c = Crawler()
        c.open('https://www.w3schools.com/')
        filtered_results = c.xpath('//p').filter(filters={'class': 'w3-xlarge'})


Using retries:
----------------

.. code-block:: python

        c = Crawler()
        # sets max_retries to 2 means that after there will be max two attempts to open url
        # if first attempt will fail, wait 1 second and try again, second attempt wait 2 seconds
        # and then try again
        c.max_retries = 2
        c.open('http://www.delver.cg/404')


Use case 1: Scraping Steam Specials using XPath
----------------

.. code-block:: python

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


Use case 2: Box office mojo daily movies (simple tables scraping out of the box)
----------------

.. code-block:: python

    from pprint import pprint
    from delver import Crawler

    c = Crawler(absolute_links=True)
    c.logging = True
    c.useragent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    c.open("http://www.boxofficemojo.com/daily/")
    pprint(c.tables())


Use case 3: User login
----------------

.. code-block:: python


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
