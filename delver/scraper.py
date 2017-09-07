# -*- coding: utf-8 -*-

from lxml.html import HtmlElement

from .helpers import table_to_dict, filter_element


class Scraper:
    """Scraping methods for `Crawler`
    """

    def __init__(self, *args, **kwargs):
        self.current_results = []

    def css(self, selector):
        """Wraps lxml parser css method"""
        results = self._parser.css(selector)
        if not isinstance(results, list):
            results = [results]
        self.current_results = ResultsList(results)
        return self.current_results

    def xpath(self, path):
        """Wraps lxml parser xpath method"""
        results = self._parser.xpath(path)
        if not isinstance(results, list):
            results = [results]
        self.current_results = ResultsList(results)
        return self.current_results

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
        self.current_results = ResultsList(
            list(
                self.current_parser().find_links(
                    tags,
                    filters,
                    match
                ).keys()
            )
        )
        return self.current_results

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


class ResultsList:

    __slots__ = ['results']

    def __init__(self, results):
        self.results = results or []

    def __getattr__(self, item):
        return getattr(self.results, item)

    def __len__(self):
        return self.results.__len__()

    def __getitem__(self, item):
        return self.results.__getitem__(item)

    def filter(self, tags=None, filters=None, match='EQUAL', custom_attrs=None):
        """Filters results list. Item in a list should be instances of `HtmlElement`.
        This method is to narrow result list of scraped elements. It's recommended to use this
        method on relatively small amount of results. It can be done by appropriate use of
        xpath and css selectors.

        :param tags: allowed html tags (like 'style', 'link', 'script', 'a')
        :param filters: dictionary of filters, possible values: id, text, title, class
        :param match: type of matching, possible values: 'IN', 'NOT_IN', 'EQUAL', 'NOT_EQUAL'
        :param custom_attrs: custom attrs could be added to filters, like `src, alt` for example
        :return: list of dicts
        """
        tags = tags or []
        filters = filters or {}
        filtered_results = []
        for item in self.results:
            if isinstance(item, HtmlElement):
                matched = filter_element(
                    item,
                    tags=tags,
                    filters=filters,
                    match=match,
                    custom_attrs=custom_attrs
                )
                if matched:
                    filtered_results.append(matched)
        return filtered_results

    def strip(self):
        return [result.strip() for result in self.results]
