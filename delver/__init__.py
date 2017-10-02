# -*- coding: utf-8 -*-

from .crawler import Crawler
from .exceptions import CrawlerError
from .proxies import ProxyPool
from .settings import setup_logging

setup_logging()
