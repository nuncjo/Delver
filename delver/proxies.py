# -*- coding: utf-8 -*-

import asyncio
from concurrent.futures import ThreadPoolExecutor

import requests

from .helpers import ForcedInteger


class Proxy:
    """Proxy object

    Wraps proxy ip address like "110.136.228.250:80" to object. Provides testing methods.

    """
    timeout = ForcedInteger('timeout')

    def __init__(self, proxy, _type=None, test_url=None, timeout=None):
        """Proxy initialization

        :param proxy: ip address like "110.136.228.250:80"
        :param _type: type of proxy
        :param test_url: url used during proxy testing
        :param timeout: max number of seconds to complete request
        """
        self.address = proxy
        self.working = True
        self._type = _type
        self._test_url = test_url or 'https://httpbin.org/ip'
        self._timeout = timeout or 15
        self._errors = 0

    def test(self):
        """ Test if proxy works.

        Loads custom page through proxy and checks if proxy ip address is in the response.

        :return: bool test result
        """
        request = self.proxy_request()
        self.working = (
            request.status_code == 200
            and self.address in request.json().get('origin', '')
        )
        self._errors += bool(self.working)
        return self.working

    def proxy_request(self):
        return requests.get(
            self._test_url,
            proxies={
                'http': 'http://{}'.format(self.address),
                'https': 'https://{}'.format(self.address),
            },
            timeout=self._timeout
        )

    def __repr__(self):
        return '<Proxy(address={}, working={})>'.format(self.address, self.working)


class ProxyPool:
    """Pool for handling proxies list.

    Allows to load, check and in generally manage proxies.

    Usage::

    >>> proxies = [
    ...     "110.136.228.250:80",
    ...     "166.78.156.247:80",
    ...     "173.234.216.40:21320"
    ... ]
    >>> proxy_pool = ProxyPool()
    >>> proxy_pool.load_proxies(proxies, test=False)
    >>> len(list(proxy_pool.working()))
    3

    .. todo:: Add loading from file and adding, removing single items
    """
    def __init__(self, workers=10):
        """ ProxyPool initialization

        :param workers: max workers number for executor
        """
        self._proxies = []
        self._executor = ThreadPoolExecutor(max_workers=workers)
        self._loop = None

    def __getattr__(self, name):
        """Magically extends ProxyPool methods of list methods like append, insert, sort etc.

        :param name: attribute name
        :return: attribute of list
        """
        return getattr(self._proxies, name)

    def load_proxies(self, proxies, test=False):
        """ Loads proxies. Extends pool <Proxy> list.

        :param proxies:
        :param test:
        :return:
        """
        self._loop = asyncio.get_event_loop()
        self._proxies.extend(
            self._loop.run_until_complete(self.tasks_from_list(proxies, test=test))
        )
        self._loop.close()

    async def tasks_from_list(self, proxies, test=False):
        """ Prepares list of tasks and runs them in executor.

        :param proxies: list of proxies
        :param test: test if works or not
        :return: list of <Proxy> objects
        """
        tasks = [
            self._loop.run_in_executor(self._executor, self.load_proxy, address, test)
            for address in proxies
        ]
        completed, pending = await asyncio.wait(tasks)
        return [task.result() for task in completed]

    async def tasks_from_file(self, proxies, test=False):
        raise NotImplementedError

    def working(self):
        return WorkingProxyList(proxies=self._proxies)

    def __iter__(self):
        return self._proxies.__iter__()

    def __len__(self):
        return len(self._proxies)

    def __getitem__(self, item):
        return self._proxies[item]

    def load_proxy(self, address, test=False):
        """ Makes <Proxy> object from ip address.

        :param address: proxy address "110.136.228.250:80"
        :param test: test if works or not
        :return: <Proxy> object
        """
        try:
            proxy = Proxy(address)
            if test:
                proxy.test()
        except Exception as err:
            proxy.working = False
            print(repr(err))
        finally:
            return proxy


class ProxyList:

    def __init__(self, proxies=None):
        self._proxies = proxies or []


class WorkingProxyList(ProxyList):

    def __iter__(self):
        return (proxy for proxy in self._proxies if proxy.working)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
