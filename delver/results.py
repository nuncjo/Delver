# -*- coding: utf-8 -*-

from lxml.html import HtmlElement

from .helpers import filter_element


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
