#!/usr/bin/env python3
import argparse
import logging
import math
import os
import sys
import yaml
import json
from datetime import datetime

import pytz
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.graphql import GraphQLApp
import graphene

from models import (
    RunInModel,
    RunOutModel,
    ListOutModel,
)

from lib_graphql import Query


def cfg_get(config):
    def_config_file = open('config_default.yaml', 'r')
    def_config = yaml.safe_load(def_config_file)
    return {**def_config, **config}


def run_get(name):
    module_path = f'{name}'
    logger.info('Module: %s', module_path)
    module = __import__(module_path)
    return getattr(module, 'run')


# ################################################### SETUP AND ARGUMENT PARSING
# ##############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, f'{dir_path}/modules')
config = {
    'proxy_prefix': os.getenv('PROXY_PREFIX', ''),
    'server': {
        'host': os.getenv('HOST', '127.0.0.1'),
        'port': int(os.getenv('PORT', '5000')),
        'log_level': os.getenv('LOG_LEVEL', 'info'),
        'timeout_keep_alive': 0,
    },
    'log_level': 'info',
}
config = cfg_get(config)
print("Applied configuration:")
print(json.dumps(config, indent=2))

VERSION = 1
START_TIME = datetime.now(pytz.utc)


# ############################################################### SERVER ROUTES
# #############################################################################

app = FastAPI(root_path=config['proxy_prefix'])
app.add_route("/gql", GraphQLApp(schema=graphene.Schema(query=Query)))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ############################################################### SERVER ROUTES
# #############################################################################
@app.get("/")
def root():
    """
    Query service status
    """
    now = datetime.now(pytz.utc)
    delta = now - START_TIME
    delta_s = math.floor(delta.total_seconds())
    return {
        'all_systems': 'nominal',
        'timestamp': now,
        'start_time': START_TIME,
        'uptime': f'{delta_s} seconds | {divmod(delta_s, 60)[0]} minutes | {divmod(delta_s, 86400)[0]} days',
        'api_version': VERSION,
    }


@app.get('/list', response_model=ListOutModel)
def list():
    """
    List available algorithms, and optionaly their arguments and types
    """
    return {
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': [
            'test'
        ]
    }


@app.post('/run', response_model=RunOutModel)
def run(data: RunInModel):
    """
    Run selected algorithms and techniques on submitted text
    """
    plugins = config['algorithms']
    result = data.text
    log_lines = []
    try:
        for algo in data.algo_list:
            if algo.id not in plugins:
                raise RuntimeError("Method not available")
            definition = plugins[algo.id]
            for p in definition['params']:
                if p not in algo.params:
                    raise RuntimeError(f"Required parameter {p} not provided")
            run = run_get(algo.id)
            result, log = run(result, algo.params)
            log_lines = log_lines + log

        return {
            '_v': VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'text': result,
            'log': json.dumps({'lines': log_lines}),
        }

    except Exception as e:
        logger.exception(e)
        return {
            '_v': VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'text': data.text,
            'log': json.dumps({'error': f"Error occured: {str(e)}"}),
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Matching server process')
    parser.add_argument('--config', dest='config', help='config file', default=None)
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.getLevelName('DEBUG'))
        logger.debug('Debug activated')
        config['log_level'] = 'debug'
        config['server']['log_level'] = 'debug'
        logger.debug('Arguments: %s', args)

    uvicorn.run(
        app,
        **config['server']
    )
