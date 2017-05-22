# -*- coding: utf-8 -*-


class Scraper:
    """Scraping methods for `Crawler`
    """
    def css(self, selector):
        return self._parser.css(selector)

    def xpath(self, path):
        return self._parser.xpath(path)

    def regexp(self, selectors=None):
        raise NotImplementedError

    def title(self):
        raise NotImplementedError

    def emails(self):
        raise NotImplementedError

    def copyrights(self):
        raise NotImplementedError

    def powered_py(self):
        raise NotImplementedError

    def images(self):
        raise NotImplementedError

    def tables(self):
        raise NotImplementedError

    def youtube(self):
        raise NotImplementedError
