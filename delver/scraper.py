# -*- coding: utf-8 -*-

import asyncio
from contextlib import contextmanager
from .decorators import results_list
from .results import ResultsList
from .helpers import table_to_dict, filter_element


class Scraper:
    """Scraping methods for `Crawler`
    """
    HTML_REQUESTS_METHODS = ('search', 'render', 'page')

    def __init__(self, *args, **kwargs):
        self.current_results = []

    def __getattr__(self, item):
        """Wraps some chosen methods (HTML_REQUESTS_METHODS) from requests_html ``HTML`` object

        :param item: method name
        :return: value of the attribute
        """
        if item in self.HTML_REQUESTS_METHODS:
            return getattr(self._current_response.html, item)
        return super().__getattr__(item)

    @contextmanager
    def rendered(self):
        self.render(keep_page=True)
        yield self.page
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.page.close())

    @property
    def html(self):
        return self._current_response.html

    @property
    def next_page(self):
        return self._current_response.html.next

    @results_list
    def pq(self, selector):
        """PyQuery selectors"""
        return self._current_response.html.pq(selector)

    @results_list
    def css(self, selector):
        """Wraps lxml parser css method"""
        return self._parser.css(selector)

    @results_list
    def xpath(self, path):
        """Wraps lxml parser xpath method"""
        return self._parser.xpath(path)

    def regexp(self, selectors=None):
        """Not implemented due the poor performance."""
        raise NotImplementedError

    def title(self):
        """Scrapes website titles

        :return: list
        """
        return self._parser.xpath('//title/text()')

    def links(self, tags=None, filters=None, match='EQUAL'):
        """Find all links on current page using given criteria

        Usage::

            >>> c = Crawler()
            >>> c.open('https://httpbin.org/links/10/0')
            <Response [200]>
            >>> links = c.links(
            ...     tags = ('style', 'link', 'script', 'a'),
            ...     filters = {
            ...         'text': '7'
            ...     },
            ...     match='NOT_EQUAL'
            ... )
            >>> len(links)
            8

        :param tags: allowed html tags (like 'style', 'link', 'script', 'a')
        :param filters: dictionary of filters, possible values: id, text, title, class
        :param match: type of matching, possible values: 'IN', 'NOT_IN', 'EQUAL', 'NOT_EQUAL'
        :return:
        """
        return ResultsList(
            list(self.current_parser().find_links(tags, filters, match).keys())
        )

    def images(self, filters=None, match='EQUAL'):
        """ Scraping images using filtering

        :param tags: allowed html tags (like 'style', 'link', 'script', 'a')
        :param filters: dictionary of filters, possible values: id, text, title, class
        :param match: type of matching, possible values: 'IN', 'NOT_IN', 'EQUAL', 'NOT_EQUAL'
        :return:
        """
        images = []
        filters = filters or {}
        for image in self._parser.xpath('//img'):
            src = image.attrib.get('src')
            if src:
                matched = filter_element(
                    image,
                    filters=filters,
                    match=match,
                    custom_attrs=['alt', 'src']
                )
                if matched:
                    images.append(src)
        self.current_results = ResultsList(images)
        return self.current_results

    def tables(self):
        """Scrapes tables to list of dicts. Works only with simple flat tables with <th> headers.

        :return: list of defaultdicts
        """
        return [
            table_to_dict(table)
            for table in self._parser.xpath('//table')
        ]
