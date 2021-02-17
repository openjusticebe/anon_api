import operator
import os
from functools import reduce

import yaml

from .deps import logger


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


class ConfigClass:
    """
    Application-wide config object
    """
    _config = {
        'proxy_prefix': os.getenv('PROXY_PREFIX', ''),
        'server': {
            'host': os.getenv('HOST', '127.0.0.1'),
            'port': int(os.getenv('PORT', '5000')),
            'log_level': os.getenv('LOG_LEVEL', 'info'),
            'timeout_keep_alive': 0,
        },
        'tika_ocr': {
            'host': os.getenv('TIKA_OCR_HOST', '127.0.0.1'),
            'port': os.getenv('TIKA_OCR_PORT', 9998),
            'version': '1.24.1'
        },
        'tika': {
            'host': os.getenv('TIKA_HOST', '127.0.0.1'),
            'port': os.getenv('TIKA_PORT', 9998),
            'version': '1.24.1'
        },
        'pyghotess': {
            'host': os.getenv('PGS_HOST', '127.0.0.1'),
            'port': os.getenv('PGS_PORT', 5501),
            'method': 'websocket',
            'version': '3'
        },
        'ocr_method': os.getenv('OCR_METHOD', 'pyghotess'),
        'log_level': 'info',
        'ttl_parse_seconds': 60,
        'ttl_result_seconds': 600,
        'algorithms': {
            'anon_trazor': {
                'description': 'pseudonymisation par SaaS (textrazor)',
                'url': 'https://www.textrazor.com/',
                'params': [],
                'env_required': []
            },
            'anon_bert': {
                'description': 'pseudonymisation par Machine-Learning (BERT)',
                'url': 'https://github.com/openjusticebe/anon_torch_bert',
                'params': [],
                'env_required': [
                    'ANON_BERT_HOST'
                ]
            }
        }
    }

    def merge(self, cfg):
        self._config = {**self._config, **cfg}

    def dump(self):
        logger.debug('config: %s', yaml.dump(self._config, indent=2))

    def key(self, k):
        if isinstance(k, list):
            return get_by_path(self._config, k)
        return self._config.get(k, False)

    def set(self, k, v):
        if isinstance(k, list):
            set_by_path(self._config, k, v)
        else:
            self._config[k] = v


config = ConfigClass()
