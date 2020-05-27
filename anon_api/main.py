#!/usr/bin/env python3
import argparse
import logging
import math
import os
from datetime import datetime

import pytz
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from models import (
    RunInModel,
    RunOutModel,
    ListOutModel,
)


# ################################################### SETUP AND ARGUMENT PARSING
# ##############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())
config = {
    'proxy_prefix': os.getenv('PROXY_PREFIX', '/'),
    'server': {
        'host': os.getenv('HOST', '127.0.0.1'),
        'port': int(os.getenv('PORT', '5000')),
        'log_level': os.getenv('LOG_LEVEL', 'info'),
    },
    'log_level': 'info',
}

VERSION = 1
START_TIME = datetime.now(pytz.utc)

app = FastAPI(openapi_prefix=config['proxy_prefix'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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

    return {
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'text': data.text,
        'log': '{}',
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Matching server process')
    parser.add_argument('--config', dest='config', help='config file', default=None)
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()
    if args.debug:
        logger.debug('Debug activated')
        config['log_level'] = 'debug'
        config['server']['log_level'] = 'debug'
        logger.debug('Arguments: %s', args)

    uvicorn.run(
        app,
        **config['server']
    )
