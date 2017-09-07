# -*- coding:utf-8 -*-

from urllib.parse import urlparse

from lxml import html
from lxml.html.clean import Cleaner

from .forms import FormWrapper
from .helpers import (
    match_form,
    filter_element
)


class HtmlParser:
    """ Parses response content string to valid html using `lxml.html`
    """

    def __init__(self, response, session=None, use_cleaner=None, cleaner_params=None):
        self._html_tree = html.fromstring(response.content)
        self.links = {}
        self._forms = []
        self._cleaner = Cleaner(**cleaner_params) if use_cleaner else None
        self._session = session
        self._url = response.url

    def make_links_absolute(self):
        """Makes absolute links http://domain.com/index.html from the relative ones /index.html
        """
        parsed_url = urlparse(self._url)
        self._html_tree.make_links_absolute(
            '{url.scheme}://{url.netloc}/'.format(url=parsed_url),
            resolve_base_href=True
        )

    def find_links(self, tags=None, filters=None, match='EQUAL'):
        """ Find links and iterate through them checking if they are matching given filters and
        tags

        usage::

        >>> import requests
        >>> response = requests.get('https://httpbin.org/links/10/0')
        >>> tags = ['style', 'link', 'script', 'a']
        >>> parser = HtmlParser(response)
        >>> links = parser.find_links(tags)
        >>> len(links)
        9
        """
        filters = filters or {}
        tags = tags or ['a']
        for link, _, url, _ in self._html_tree.iterlinks():
            matched = filter_element(
                link,
                tags=tags,
                filters=filters,
                match=match
            )
            if matched:
                self.links[url] = matched
        return self.links

    def find_forms(self, filters=None):
        """ Find forms and wraps them with class::`<FormWrapper>` object

        usage::

        >>> import requests
        >>> response = requests.get('https://httpbin.org/forms/post')
        >>> parser = HtmlParser(response)
        >>> forms = parser.find_forms()
        >>> len(forms)
        1
        """
        filters = filters or {}
        self._forms = []
        for form in self._html_tree.forms:
            wrapped_form = FormWrapper(form, session=self._session, url=self._url)
            if match_form(wrapped_form, filters):
                self._forms.append(wrapped_form)
        return self._forms

    def xpath(self, path):
        """Select elements using xpath selectors"""
        return self._html_tree.xpath(path)

    def css(self, selector):
        """Select elements by css selectors"""
        return self._html_tree.cssselect(selector)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
