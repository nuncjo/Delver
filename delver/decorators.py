# -*- coding: utf-8 -*-

from functools import wraps

from .exceptions import HistoryError


def with_history(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[0]._history:
            return func(*args, **kwargs)
        else:
            raise HistoryError("Crawler history is off.")
    return wrapper
