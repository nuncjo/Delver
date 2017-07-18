Delver
========================

Programmatic web browser/crawler in Python. Alternative to Machanize, RoboBrowser, MechanicalSoup
and others but with cleaner more pythonic and modern API. Projects like Mechanize were built on top on
api taken from Perl language. Delver won't use BeautifulSoup but strict power of Request and Lxml.

.. code-block:: bash

    $ pip install Delver

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
