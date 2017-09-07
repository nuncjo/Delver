# -*- coding:utf-8 -*-

import os
import json
import logging.config


def setup_logging(default_path='logging.json', default_level=logging.ERROR):
    path = default_path
    if os.path.exists(path):
        with open(path) as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
