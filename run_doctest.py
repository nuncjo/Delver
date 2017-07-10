# -*- coding:utf-8 -*-

import doctest
from delver import (
    crawler,
    forms,
    helpers,
    parser,
    proxies
)

doctest.testmod(crawler)
doctest.testmod(forms)
doctest.testmod(helpers)
doctest.testmod(parser)
doctest.testmod(proxies)
