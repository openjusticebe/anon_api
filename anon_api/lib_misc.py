import calendar
import logging
import os
from collections import namedtuple
from datetime import datetime

import pytz
import yaml

logger = logging.getLogger(__name__)
DocParse = namedtuple('DocAction', ['ref', 'file', 'ocr', 'ttl'])
DocResult = namedtuple('DocResult', ['ref', 'key', 'value', 'ttl'])


def check_envs(env_list):
    return all(os.getenv(e) for e in env_list)


def get_now():
    now = datetime.now(pytz.utc)
    return calendar.timegm(now.utctimetuple())


def run_get(name):
    module_path = f'{name}'
    logger.info('Module: %s', module_path)
    module = __import__(module_path)
    return getattr(module, 'run')


def parse_get(name):
    module_path = f'{name}'
    logger.info('Module: %s', module_path)
    module = __import__(module_path)
    return getattr(module, 'parse')
