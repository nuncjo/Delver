# -*- coding: utf-8 -*-

from lxml.html import HtmlElement

from .helpers import table_to_dict, filter_element


class Scraper:
    """Scraping methods for `Crawler`
    """

    def css(self, selector):
        """Wraps lxml parser css method"""
        results = self._parser.css(selector)
        if not isinstance(results, list):
            results = [results]
        return ResultsList(results)

    def xpath(self, path):
        """Wraps lxml parser xpath method"""
        results = self._parser.xpath(path)
        if not isinstance(results, list):
            results = [results]
        return ResultsList(results)

    def regexp(self, selectors=None):
        """Not implemented due the poor performance."""
        raise NotImplementedError

    def title(self):
        """Scrapes website titles

        :return: list
        """
        return self._parser.xpath('//title/text()')

    def images(self, filters=None, match='EQUAL'):
        """ Scraping images using filtering

        :param tags: allowed html tags (like 'style', 'link', 'script', 'a')
        :param filters: dictionary of filters, possible values: id, text, title, class
        :param match: type of matching, possible values: 'IN', 'NOT_IN', 'EQUAL', 'NOT_EQUAL'
        :return:
        """
        images = {}
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
                    images[src] = matched
        return images

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
