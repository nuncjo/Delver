# -*- coding:utf-8 -*-

from urllib.parse import urlparse

from lxml import html
from lxml.html.clean import Cleaner

from .forms import FormWrapper
from .helpers import (
    match_form,
    match_link
)


class HtmlParser:

    def __init__(self, response, session=None, use_cleaner=None, cleaner_params=None):
        self._html_tree = html.fromstring(response.content)
        self._links = {}
        self._forms = []
        self._cleaner = Cleaner(**cleaner_params) if use_cleaner else None
        self._session = session
        self._url = response.url

    def make_links_absolute(self):
        parsed_url = urlparse(self._url)
        self._html_tree.make_links_absolute(
            '{url.scheme}://{url.netloc}/'.format(uri=parsed_url),
            resolve_base_href=True
        )

    def find_links(self, tags=None, filters=None, match='EQUAL'):
        """
        >>> import requests
        >>> response = requests.get('https://httpbin.org/links/10/0')
        >>> tags = ['style', 'link', 'script', 'a']
        >>> parser = HtmlParser(response)
        >>> parser.find_links(tags)
        """
        filters = filters or {}
        tags = tags or ['a']
        for link, attribute, url, pos in self._html_tree.iterlinks():
            if link.tag in tags:
                link_data = {
                    'id': link.attrib.get('id', ''),
                    'text': link.text,
                    'title': link.attrib.get('title', ''),
                    'class': link.attrib.get('class', '')
                }
                if filters:
                    if match_link(link_data, filters, match=match):
                        self._links[url] = link_data
                else:
                    self._links[url] = link_data
        return self._links

    def find_forms(self, filters=None):
        """
        >>> import requests
        >>> response = requests.get('https://httpbin.org/forms/post')
        >>> parser = HtmlParser(response)
        >>> forms = parser.find_forms()
        """
        self._forms = []
        for form in self._html_tree.forms:
            wrapped_form = FormWrapper(form, session=self._session, url=self._url)
            if match_form(wrapped_form, filters):
                self._forms.append(wrapped_form)
        return self._forms

    def xpath(self, path):
        return self._html_tree.xpath(path)

    def css(self, selector):
        return self._html_tree.cssselect(selector)


class ContentExtractor:
    """Parsing of additional html elements
     TODO: http://lxml.de/tutorial.html#incremental-parsing
    """
    def find_tables(self):
        raise NotImplementedError

    def find_microformats(self):
        raise NotImplementedError

    def find_files(self, extensions):
        raise NotImplementedError

    def find_images(self):
        raise NotImplementedError

    def html_diff(self):
        raise NotImplementedError
