# -*- coding: utf-8 -*-

from .helpers import table_to_dict


class Scraper:
    """Scraping methods for `Crawler`
    """

    def css(self, selector):
        """Wraps lxml parser css method"""
        return self._parser.css(selector)

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

    def images(self):
        """ Scrapes images paths

        :return: list
        """
        return self._parser.xpath('//img/@src')

    def tables(self):
        """Scrapes tables to list of dicts. Works only with simple flat tables with <th> headers.

        :return: list of defaultdicts
        """
        return [
            table_to_dict(table)
            for table in self._parser.xpath('//table')
        ]
