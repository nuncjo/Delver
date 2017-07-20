# -*- coding: utf-8 -*-

from .helpers import table_to_dict, filter_element


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

    def images(self, tags=None, filters=None, match='EQUAL'):
        """ Scraping images using filtering

        :param tags: allowed html tags (like 'style', 'link', 'script', 'a')
        :param filters: dictionary of filters, possible values: id, text, title, class
        :param match: type of matching, possible values: 'IN', 'NOT_IN', 'EQUAL', 'NOT_EQUAL'
        :return:
        """
        images = {}
        filters = filters or {}
        tags = tags or ['img']
        for image in self._parser.xpath('//img'):
            src = image.attrib.get('src')
            if src:
                matched = filter_element(
                    image,
                    tags=tags,
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
