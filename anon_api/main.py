#!/usr/bin/env python3
import argparse
import asyncio
import logging
import math
import os
import sys
from datetime import datetime

import graphene
import pytz
import toml
import uvicorn
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from starlette.middleware.cors import CORSMiddleware

import anon_api.lib_workers as worker
from anon_api.lib_graphql import Query
from anon_api.models import ListOutModel

from .deps import API_VERSION, QUEUES, logger
from .lib_cfg import config
from .routers import anonymise, extract

# ####################################################################### SETUP
# ##############################################################################
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, f'{dir_path}/modules')

VERSION = "0.3.0"
START_TIME = datetime.now(pytz.utc)

tags_metadata = [
    {
        "name": "extract",
        "description": "Text content extraction"
    },
    {
        "name": "parse",
        "description": "Text anonymisation and pseudonymisation"
    },
]

# ############################################################### SERVER CONFIG
# #############################################################################

app = FastAPI(root_path=config.key('proxy_prefix'), openapi_tags=tags_metadata)
app.add_route("/gql", GraphQLApp(schema=graphene.Schema(query=Query)))

# Include sub routes
app.include_router(extract.router)
app.include_router(anonymise.router)

# Server config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    QUEUES["parseIn"] = asyncio.Queue()
    QUEUES["ocrIn"] = asyncio.Queue()
    QUEUES["parseOut"] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    # Add doc parsing worker to event loop
    loop.create_task(worker.doc_parser(
        config,
        QUEUES["parseIn"],
        QUEUES["ocrIn"],
        QUEUES["parseOut"])
    )

    # Add doc ocr worker to event loop
    if config.key('ocr_method') == 'tika':
        loop.create_task(worker.tika_ocr(
            config,
            QUEUES["ocrIn"],
            QUEUES["parseOut"])
        )
    elif config.key('ocr_method') == 'pyghotess':
        loop.create_task(worker.pyghotess_ocr(
            config,
            QUEUES["ocrIn"],
            QUEUES["parseOut"])
        )
    else:
        logger.critical('OCR method %s not supported, crashing', config.key('ocr_method'))
        raise RuntimeError('Bad or missing OCR method')


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
        'version': VERSION,
        'api_version': API_VERSION,
    }


@app.get('/list', response_model=ListOutModel)
def list():
    """
    List available algorithms, and optionaly their arguments and types
    """
    return {
        '_v': API_VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': [
            'test'
        ]
    }


# ##################################################################### STARTUP
# #############################################################################
def main():

    parser = argparse.ArgumentParser(description='Matching server process')
    parser.add_argument('--config', dest='config', help='config file', default=None)
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    # XXX: Lambda is a hack : toml expects a callable
    if args.config:
        t_config = toml.load(['config_default.toml', args.config])
    else:
        t_config = toml.load('config_default.toml')

    config.merge(t_config)

    if args.debug:
        logger.setLevel(logging.getLevelName('DEBUG'))
        logger.debug('Debug activated')
        config.set('log_level', 'debug')
        config.set(['server', 'log_level'], 'debug')
        logger.debug('Arguments: %s', args)
        config.dump()

    uvicorn.run(
        app,
        **config.key('server')
    )


if __name__ == "__main__":
    main()
