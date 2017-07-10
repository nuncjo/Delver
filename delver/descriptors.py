# -*- coding: utf-8 -*-


class Useragent:

    def __get__(self, instance, owner):
        return instance.__dict__['_useragent']

    def __set__(self, instance, value):
        """Sets useragent. Useragent set in that way is used for all crawler requests
        unless it is overridden in request kwargs or changed.
        """
        instance.__dict__['_useragent'] = value
        instance.__dict__['_headers']['user-agent'] = value


class Proxy:

    def __get__(self, instance, owner):
        return instance.__dict__['_proxy']

    def __set__(self, instance, value):
        """Sets proxy. Proxy set in that way is used for all crawler requests
        unless it is overridden in request kwargs or changed.
        """
        instance.__dict__['_proxy'] = {
            'http': 'http://{}'.format(value),
            'https': 'https://{}'.format(value)
        }


class Headers:

    def __get__(self, instance, owner):
        return instance.__dict__['_headers']

    def __set__(self, instance, value):
        """Sets headers. Headers set in that way are used for all crawler requests
        unless it is overridden in request kwargs or changed.
        """
        instance.__dict__['_headers'] = value
