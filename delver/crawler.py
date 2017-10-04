# -*- coding: utf-8 -*-

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import randrange

from collections import namedtuple, deque
from copy import deepcopy
from urllib.parse import urljoin, urlparse

import requests

from .decorators import with_history
from .exceptions import CrawlerError
from .helpers import ForcedInteger
from .parser import HtmlParser
from .scraper import Scraper
from .descriptors import (
    Useragent,
    Proxy,
    Headers
)

PARSERS = {
    'text/html': HtmlParser,
    'text/plain': HtmlParser,
    'text/json': HtmlParser,
    'application/xml': HtmlParser,
    'application/json': HtmlParser
}


class Crawler(Scraper):
    """Browser mimicking object. Mostly wrapper on Requests and Lxml libraries.

    :param history: (optional) bool, turns off/on history usage in Crawler
    :param max_history: (optional) int, max items held in history
    :param absolute_links: (optional) bool, makes always all links absolute


    Features:

    - To some extent, acts like a browser

    - Allows visiting pages, form posting, content scraping, cookie handling etc.

    - Wraps ``requests.Session()``


    Simple usage::

        >>> c = Crawler()
        >>> response = c.open('https://httpbin.org/html')
        >>> response.status_code
        200


    Form submit::

        >>> c = Crawler()
        >>> response = c.open('https://httpbin.org/forms/post')
        >>> forms = c.forms()

        Filling up fields values:
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

        Checking if form post ended with success:
        >>> c.submit_check(
        ...    form,
        ...    phrase="Ruben Rybnik",
        ...    url='https://httpbin.org/post',
        ...    status_codes=[200])
        True


    Form file upload::

        >>> c = Crawler()
        >>> c.open('http://cgi-lib.berkeley.edu/ex/fup.html')
        <Response [200]>
        >>> forms = c.forms()
        >>> upload_form = forms[0]
        >>> upload_form.fields = {
        ...    'note': 'Text file with quote',
        ...    'upfile': open('test/test_file.txt', 'r')
        ... }
        >>> c.submit(upload_form, action='http://cgi-lib.berkeley.edu/ex/fup.cgi')
        <Response [200]>
        >>> c.submit_check(
        ...    upload_form,
        ...    phrase="road is easy",
        ...    status_codes=[200]
        ... )
        True

    Cookies handling::

        >>> c = Crawler()
        >>> c.open('https://httpbin.org/cookies', cookies={
        ...     'cookie_1': '1000101000101010',
        ...     'cookie_2': 'ABABHDBSBAJSLLWO',
        ... })
        <Response [200]>

    Find links::

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

    Find images::

        >>> c = Crawler()
        >>> c.open('https://www.python.org/')
        <Response [200]>

        First image path with 'python-logo' in string:
        >>> next(
        ...     image_path for image_path in c.images()
        ...     if 'python-logo' in image_path
        ... )
        'https://www.python.org/static/img/python-logo.png'

    Download file::

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

        >>> c = Crawler()
        >>> c.open('https://xkcd.com/')
        <Response [200]>
        >>> full_images_urls = [c.join_url(src) for src in c.images()]
        >>> downloaded_files = c.download_files('test', files=full_images_urls)
        >>> len(full_images_urls) == len(downloaded_files)
        True

    Traversing through history::

        >>> c = Crawler()
        >>> c.open('http://quotes.toscrape.com/')
        <Response [200]>
        >>> tags_links = c.links(filters={'class': 'tag'})
        >>> c.follow(tags_links[0])
        <Response [200]>
        >>> c.follow(tags_links[1])
        <Response [200]>
        >>> c.follow(tags_links[2])
        <Response [200]>
        >>> history = c.history()
        >>> c.back()
        >>> c.get_url() == history[-2].url
        True
    """

    useragent = Useragent()
    proxy = Proxy()
    headers = Headers()
    max_retries = ForcedInteger('max_retries')

    def __init__(self, history=True, max_history=5, absolute_links=True):
        """Crawler initialization

        :param history: bool, turns on/off history handling
        :param max_history: max items stored in flow
        :param absolute_links: globally make links absolute
        """
        super().__init__(
            history=history,
            max_history=max_history,
            absolute_links=absolute_links
        )
        self._session = requests.Session()
        self._history = history
        self._max_history = max_history
        self._flow = deque(maxlen=self._max_history)
        self._index = 0
        self._parser = None
        self._current_response = None
        self._absolute_links = absolute_links
        self._useragent = None
        self._headers = {}
        self._proxy = {}
        self._loop = None
        self._executor = None
        self._max_retries = 0
        self._retries = 0
        self._logging = False
        self._logger = None
        self._random_timeout = None

    @property
    def logging(self):
        return self._logging

    @logging.setter
    def logging(self, value):
        self._logging = value
        self._logger = logging.getLogger(__name__) if value else None

    @property
    def random_timeout(self):
        return self._random_timeout

    @random_timeout.setter
    def random_timeout(self, value):
        if isinstance(value, (list, tuple)):
            self._random_timeout = value
        else:
            raise TypeError('Expected list or tuple.')

    def fit_parser(self, response):
        """Fits parser according to response type.

        :param response: class::`Response <Response>` object
        :return: matched parser object like: class::`HtmlParser <HtmlParser>` object
        """
        content_type = response.headers.get('Content-type', '')
        for _type, parser in PARSERS.items():
            if _type in content_type:
                self._parser = PARSERS[_type](response, session=self._session)
                return self._parser
        if self._logging:
            self._logger.info("Couldn't fit parser for {}.".format(content_type))

    def handle_response(self):
        """Called after request. Make operations accordng to attributes settings."""
        if self._absolute_links:
            self._parser.make_links_absolute()
        if self._history:
            self._flow.append({'parser': deepcopy(self._parser)})

    def open(self, url, method='get', **kwargs):
        """Opens url. Wraps functionality of `Session` from `Requests` library.

        :param url: visiting url str
        :param method: 'get', 'post' etc. str
        :param kwargs: additional keywords like headers, cookies etc.
        :return: class::`Response <Response>` object
        """
        self._retries = 0
        self._current_response = None
        flow_len = len(self._flow)
        if flow_len < self._max_history:
            self._index = flow_len

        self.add_customized_kwargs(kwargs)

        while True:
            try:
                self._current_response = self._session.request(method, url, **kwargs)
                if self._random_timeout:
                    time.sleep(randrange(*self._random_timeout))
                if self._logging:
                    self._logger.info(
                        'Open method: {} request: url={}, status code={}, kwargs={}  '.format(
                            method.upper(),
                            url,
                            self._current_response.status_code,
                            kwargs
                        ))
            except requests.exceptions.ConnectionError:
                self._retries += 1
                time.sleep(self._retries)
                if self.logging:
                    self._logger.error(
                        'Failed, try {}, method: {} request: url={}, kwargs={}  '.format(
                            self._retries,
                            method.upper(),
                            url,
                            kwargs
                        ))
                if self._retries >= self._max_retries:
                    raise
                continue
            break

        if self._current_response and self.fit_parser(self._current_response):
            self.handle_response()
            if self._history:
                self._flow[self._index].update({'response': deepcopy(self._current_response)})
            return self._current_response

    def add_customized_kwargs(self, kwargs):
        """Adds request keyword arguments customized by setting `Crawler`
        attributes like proxy, useragent, headers. Arguments won't be passed
        if they are already set as `open` method kwargs.
        """
        if self._proxy and 'proxies' not in kwargs:
            kwargs.update({'proxies': self._proxy})
        if self._headers and 'headers' not in kwargs:
            kwargs.update({'headers': self._headers})

    def response(self):
        """Get current response."""
        return self._current_response

    def get_url(self):
        """Get URL of current document."""
        return self._current_response.url

    def join_url(self, url_path):
        """Returns absolute_url. Path joined with url_root."""
        return urljoin(
            self._current_response.url,
            url_path
        )

    @with_history
    def back(self, step=1):
        """Go back n steps in history, and return response object"""
        if self._index - step > 0:
            self._index -= step
            self._current_response = self._flow[self._index]['response']
        else:
            raise CrawlerError("Out of history boundaries")

    @with_history
    def forward(self, step=1):
        """Go forward n steps in history, and return response object"""
        if self._index + step < self._max_history:
            self._index += step
            self._current_response = self._flow[self._index]['response']
        else:
            raise CrawlerError("Out of history boundaries")

    def follow(self, url, method='get',  **kwargs):
        """Follows url"""
        self.add_customized_kwargs(kwargs)
        return self.open(self.join_url(url), method, **kwargs)

    @with_history
    def flow(self):
        """Return flow"""
        return self._flow

    def clear(self):
        """Clears all flow, session, headers etc."""
        self._flow.clear()
        self._index = 0
        self._session.cookies.clear()
        self._headers = {}
        self._proxy = {}

    @with_history
    def history(self):
        """Return urls history and status codes"""
        Visit = namedtuple('Visited', 'url method response')
        return [
            Visit(
                history['response'].url,
                history['response'].request.method,
                history['response'].status_code
            )
            for history in self._flow
        ]

    def request_history(self):
        """Returns current request history (like list of redirects to finally accomplish request)
        """
        return self._current_response.history

    @property
    def cookies(self):
        """Wraps `RequestsCookieJar` object from requests library.

        :return: `RequestsCookieJar` object
        """
        return self._current_response.cookies

    def current_parser(self):
        """Return parser associated with current flow item.

        :return: matched parser object like: class::`HtmlParser <HtmlParser>` object
        """
        return self._flow[self._index]['parser']

    def forms(self, filters=None):
        """Return iterable over forms. Doesn't find javascript forms yet (but will be).

            example_filters = {
                'id': 'searchbox',
                'name': 'name,
                'action': 'action',
                'has_fields': ['field1', 'field2']

            }

        Usage::

            >>> c = Crawler()
            >>> response = c.open('http://cgi-lib.berkeley.edu/ex/fup.html')
            >>> forms = c.forms()
            >>> forms[0].fields['note'].get('tag')
            'input'
            """

        filters = filters or {}
        if self._history:
            return self.current_parser().find_forms(filters)
        return self._parser.find_forms(filters)

    def submit(self, form=None, action=None, data=None):
        """Submits form

        :param form: `FormWrapper` object
        :param action: custom action url
        :param data: additional custom values to submit
        :return: submit result
        """
        if form:
            action = action or form.action_url()
            values = form.form_values()
            form.append_extra_values(values, data)
            form.result = self.open(
                action,
                form.method,
                data=values,
                files=form.files,
            )
        else:
            self.direct_submit(url=action, data=data)
        return self._current_response

    def direct_submit(self, url=None, data=None):
        """Direct submit. Used when quick post to form is needed or if there are no forms found
        by the parser.

        Usage::

            >>> data = {'name': 'Piccolo'}
            >>> c = Crawler()
            >>> result = c.submit(action='https://httpbin.org/post', data=data)
            >>> result.status_code
            200

        :param url: submit url, form action url, str
        :param data: submit parameters, dict
        :return: class::`Response <Response>` object
        """
        current_url = None
        if self._current_response:
            current_url = self._current_response.url
        return self.open(
            url or current_url,
            method='post',
            data=data or {}
        )

    def submit_check(self, form, phrase=None, url=None, status_codes=None):
        """Checks if success conditions of form submit are met

        :param form: `FormWrapper` object
        :param phrase: expected phrase in text
        :param url: expected url
        :param status_codes: list of expected status codes
        :return: bool
        """
        return all([
            phrase in form.result.text if phrase else True,
            form.result.url == url if url else True,
            form.result.status_code in status_codes if status_codes else True
        ])

    def encoding(self):
        """Returns current respose encoding."""
        return self._flow[self._index].encoding

    def download(self, local_path=None, url=None, name=None):
        file_name = name or os.path.split(urlparse(url).path)[-1]
        if file_name:
            download_path = os.path.join(local_path, file_name)
            with open(download_path, 'wb') as f:
                f.write(self._session.get(url).content)
            return download_path

    def download_files(self, local_path, files=None, workers=10):
        """Download list of files in parallel.

        :param workers: number of threads
        :param local_path: download path
        :param files: list of files
        :return: list with downloaded files paths
        """
        files = files or []
        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for future in as_completed(
                    executor.submit(self.download, local_path, file)
                    for file in files
            ):
                results.append(future.result())

        return results


if __name__ == '__main__':
    import doctest
    doctest.testmod()
