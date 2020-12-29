#!/usr/bin/env python3
import argparse
import logging
import asyncio
import math
import os
import sys
import json
import requests
import uuid
from datetime import datetime

import pytz
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.graphql import GraphQLApp
import graphene

from anon_api.models import (
    RunInModel,
    RunOutModel,
    ParseInModel,
    ParseOutModel,
    ListOutModel,
)

import anon_api.lib_workers as worker

from anon_api.lib_graphql import Query

from anon_api.lib_misc import (
    DocParse,
    cfg_get,
)


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
}
config = cfg_get(config)
print("Applied configuration:")
print(json.dumps(config, indent=2))

VERSION = "0.3.0"
START_TIME = datetime.now(pytz.utc)
QUEUES = {}

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
    if config['ocr_method'] == 'tika':
        loop.create_task(worker.tika_ocr(
            config,
            QUEUES["ocrIn"],
            QUEUES["parseOut"])
        )
    elif config['ocr_method'] == 'pyghotess':
        loop.create_task(worker.pyghotess_ocr(
            config,
            QUEUES["ocrIn"],
            QUEUES["parseOut"])
        )
    else:
        logger.critical('OCR method %s not supported, crashing', config['ocr_method'])
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


@app.post('/parse', response_model=ParseOutModel)
def parse(data: ParseInModel):
    """
    Run selected algorightms, get entities and types
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
            parse = parse_get(algo.id)
            result, log = parse(result, algo.params)
            log_lines = log_lines + log

        return {
            '_v': VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'entities': json.dumps(result),
            'log': json.dumps({'lines': log_lines}),
        }

    except Exception as e:
        logger.exception(e)
        return {
            '_v': VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'entities': '{}',
            'log': json.dumps({'error': f"Error occured: {str(e)}"}),
        }


@app.post('/fileinfo/')
async def fileinfo(rawFile: UploadFile = File(...)):
    """
    Get info about file
    """
    tConf = config['tika']
    tika_server = f"http://{tConf['host']}:{tConf['port']}/meta/form"
    r = requests.post(
        tika_server,
        files={'upload': rawFile.file.read()},
        headers={'Accept': 'application/json'}
    ).json()
    chars = [int(v) for v in r.get('pdf:charsPerPage', [])]
    return {
        "language": r.get('language', None),
        "charsperpage": chars,
        "charstotal": sum(chars),
        "pages": len(chars),
        "filename": rawFile.filename,
        "content_type": rawFile.content_type,
        "size_bytes": rawFile.file.tell(),
    }


@app.post('/extract/')
async def extract(ocr: int = 0, rawFile: UploadFile = File(...)):
    """
    Extract text from provided file
    """
    ref = str(uuid.uuid4())

    docTask = DocParse(ref, rawFile, ocr == 1, datetime.now())

    QUEUES["parseIn"].put_nowait(docTask)

    return {
        'ref': ref
    }


@app.get('/extract/status')
async def status(ref: str):
    """
    Retrieve parse status from file parsing task.
    We just loop on the queue, buffering the other messages
    until we find a message of interest.

    Whatever happens, the few messages we buffered are put back
    into the queue.
    """
    buff = []
    try:
        buff = []
        while True:
            msg = QUEUES["parseOut"].get_nowait()
            if msg.ref == ref:
                break
            buff.append(msg)
        return {
            'ref': msg.ref,
            'status': msg.key,
            'value': msg.value,
            'qs': QUEUES["parseOut"].qsize()
        }
    except asyncio.queues.QueueEmpty:
        return {
            'ref': ref,
            'status': 'empty',
            'value': None,
            'qs': QUEUES["parseOut"].qsize()
        }
    finally:
        for msg in buff:
            delta = (datetime.now() - msg.ttl).total_seconds()
            if delta < config['ttl_result_seconds']:
                # Filter TTL's
                logger.info('Putting msg back in queue %s', msg.ref)
                QUEUES["parseOut"].put_nowait(msg)


# ##################################################################### STARTUP
# #############################################################################
def main():
    global config

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


if __name__ == "__main__":
    main()
