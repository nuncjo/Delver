# -*- coding: utf-8 -*-

from .crawler import Crawler
from .exceptions import CrawlerError
from .proxies import ProxyPool
from .settings import setup_logging

__version__ = '0.1.6'

setup_logging()
