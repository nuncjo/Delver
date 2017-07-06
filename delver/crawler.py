# -*- coding: utf-8 -*-

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from collections import namedtuple, deque
from copy import deepcopy
from urllib.parse import urljoin, urlparse

import requests

from .decorators import with_history
from .exceptions import CrawlerError
from .parser import HtmlParser
from .scraper import Scraper
from .descriptors import (
    Useragent,
    Proxy,
    Headers
)

PARSERS = {
    'text/html': HtmlParser,
    'text/json': HtmlParser,
    'application/xml': HtmlParser,
    'application/json': HtmlParser,
}


class Crawler(Scraper):
    """Browser mimicking object

    Features:
    - To some extent, acts like a browser
    - Allows visiting pages, form posting, content scraping, cookie handling etc.
    - Wraps ``requests.Session()``

    Usage::

    >>> c = Crawler(history=True)
    >>> response = c.open('https://httpbin.org/html')
    >>> response.status_code
    200

    """

    useragent = Useragent()
    proxy = Proxy()
    headers = Headers()

    def __init__(self, history=True, max_history=5, absolute_links=False):
        """Crawler initialization

        :param history: bool, turns on/off history handling
        :param max_history: max items stored in flow
        :param absolute_links: globally make links absolute
        """
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
        raise CrawlerError(f"Couldn't fit parser for {content_type}.")

    def setup(self):
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
        flow_len = len(self._flow)
        if flow_len < self._max_history:
            self._index = flow_len

        self.add_customized_kwargs(kwargs)
        self._current_response = self._session.request(method, url, **kwargs)

        if self.fit_parser(self._current_response):
            self.setup()
            if self._history:
                self._flow[self._index].update({'response': deepcopy(self._current_response)})
            return self._current_response

    def submit(self, url=None, data=None):
        """Direct submit. Used when quick post to form is needed or if there are no forms found by the parser.

        :param url: submit url, form action url, str
        :param data: submit parameters, dict
        :return: class::`Response <Response>` object

        Usage::

        >>> c = Crawler()
        >>> c.submit(
        ...    url=self.urls['POST'],
        ...    data={
        ...        'name': 'Piccolo'
        ...    }
        ...)
        >>> response.status_code
        200

        """
        current_url = None
        if self._current_response:
            current_url = self._current_response.url
        return self.open(
            url or current_url,
            method='post',
            data=data or {}
        )

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
        """Returns current request history (like list of redirects to finally accomplish request)"""
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

    def links(self, tags=None, filters=None, match='EQUAL'):
        return self.current_parser().find_links(tags, filters, match)

    def forms(self, filters=None):
        """Return iterable over forms. Doesn't find javascript forms yet (but will be).
        >>> c = Crawler()
        >>> response = c.open('https://httpbin.org/forms/post')
        >>> forms = c.forms(filters={'id': 'searchbox'})
        >>> forms[1].fields = {'from': 'test@xxx.com'}
        >>> forms[1].fields['from']
        'test@xxx.com'
        """
        filters = filters or {}
        if self._history:
            return self.current_parser().find_forms(filters)
        return self._parser.find_forms(filters)

    def encoding(self):
        return self._flow[self._index].encoding

    def download(self, local_path, url, name=None):
        file_name = name or os.path.split(urlparse(url).path)[-1]
        if file_name:
            download_path = os.path.join(local_path, file_name)
            with open(download_path, 'wb') as f:
                f.write(self._session.get(url).content)
            return download_path

    def download_files(self, local_path, files=None, workers=10):
        """Download list of images in parallel.

        :param workers: number of threads
        :param local_path:
        :param files: list of files
        :return:
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
