Delver
========================

Programmatic web browser/crawler in Python. Alternative to Machanize, RoboBrowser, MechanicalSoup
and others but with cleaner more pythonic and modern API. Projects like Mechanize were built on top on
api taken from Perl language. Delver won't use BeautifulSoup but strict power of Request and Lxml.
Delver will have much more features and methods usefull in scraping "out of the box".
Lots of features are still in progress.

.. code-block:: bash

    $ pip install delver

Example form submit:
----------------

.. code-block:: python

        >>> from delver import Crawler()
        >>> c = Crawler()
        >>> response = c.open('https://httpbin.org/forms/post')
        >>> forms = c.forms()

        Filling up fields values:
        >>> forms[0].fields = {
        ...    'custname': 'Ruben Rybnik',
        ...    'custemail': 'ruben.rybnik@fakemail.com',
        ...    'size': 'medium',
        ...    'topping': ['bacon', 'cheese'],
        ...    'custtel': '+48606505888'
        ... }
        >>> submit_result = forms[0].submit()
        >>> submit_result.status_code
        200

        Checking if form post ended with success:
        >>> forms[0].check(
        ...    phrase="Ruben Rybnik",
        ...    url='https://httpbin.org/forms/post',
        ...    status_codes=[200])
        True


Find links narowed by filters::
----------------

        >>> c = Crawler()
        >>> c.open('https://httpbin.org/links/10/0')
        <Response [200]>

        Links can be filtered by some html tags and filters
        like: id, text, title and class:
        >>> links = c.links(
        ...     tags = ('style', 'link', 'script', 'a'),
        ...     filters = {
        ...         'text': '7'
        ...     },
        ...     match='NOT_EQUAL'
        ... )
        >>> len(links)
        8

Download file::
----------------

        >>> import os

        >>> c = Crawler()
        >>> local_file_path = c.download(
        ...     local_path='test',
        ...     url='https://httpbin.org/image/png',
        ...     name='test.png'
        ... )
        >>> os.path.isfile(local_file_path)
        True

Download files list in parallel::
----------------

        >>> c = Crawler()
        >>> c.open('https://xkcd.com/')
        <Response [200]>
        >>> full_images_urls = [c.join_url(src) for src in c.images()]
        >>> downloaded_files = c.download_files('test', files=full_images_urls)
        >>> len(full_images_urls) == len(downloaded_files)
        True

Using xpath selectors::
----------------
        c = Crawler()
        c.open('https://httpbin.org/html')
        p_text = c.xpath('//p/text()')

Using css selectors::
----------------
        c = Crawler()
        c.open('https://httpbin.org/html')
        p_text = c.css('div')
