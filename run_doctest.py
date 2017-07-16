# -*- coding:utf-8 -*-

import os
import doctest
import shutil

from delver import (
    crawler,
    forms,
    helpers,
    parser,
    proxies
)

if __name__ == "__main__":
    os.makedirs('test', exist_ok=True)
    with open('test/test_file.txt', 'wb') as f:
        f.write(b"If the road is easy, you're likely going the wrong way..")
    doctest.testmod(crawler)
    doctest.testmod(forms)
    doctest.testmod(helpers)
    doctest.testmod(parser)
    doctest.testmod(proxies)
    shutil.rmtree('test', ignore_errors=True)
