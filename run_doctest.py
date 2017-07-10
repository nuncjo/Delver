# -*- coding:utf-8 -*-

import doctest
from delver import (
    crawler,
    forms,
    helpers,
    parser,
    proxies
)


if __name__ == "__main__":
    doctest.testmod(crawler)
    doctest.testmod(forms)
    doctest.testmod(helpers)
    doctest.testmod(parser)
    doctest.testmod(proxies)
