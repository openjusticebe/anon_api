from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import pytz
import json
from ..lib_cfg import (config)
from ..models import (
    RunInModel,
    RunOutModel,
    ParseInModel,
    ParseOutModel,
)
from ..deps import (
    # config,
    logger,
    API_VERSION,
)
from ..lib_misc import (
    run_get,
    parse_get,
)


router = APIRouter()


# ##################################### ROUTES
# ############################################

@router.post('/run', response_model=RunOutModel, tags=['parse'])
def run(data: RunInModel):
    """
    Run selected algorithms and techniques on submitted text
    """
    plugins = config.key('algorithms')
    result = data.text
    log_lines = []
    try:
        for algo in data.algo_list:
            if algo.id not in plugins:
                raise RuntimeError("Method not available")
            definition = plugins[algo.id]
            if definition['params']:
                for p in definition['params']:
                    if p not in algo.params:
                        raise RuntimeError(f"Required parameter {p} not provided")
            run = run_get(algo.id)
            result, log = run(result, algo.params)
            log_lines = log_lines + log

        return {
            '_v': API_VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'text': result,
            'log': json.dumps({'lines': log_lines}),
        }

    except Exception as e:
        logger.exception(e)
        return {
            '_v': API_VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'text': data.text,
            'log': json.dumps({'error': f"Error occured: {str(e)}"}),
            'received': data,
        }


@router.post('/parse', response_model=ParseOutModel, tags=['parse'])
def parse(data: ParseInModel):
    """
    Run selected algorightms, get entities and types
    """
    plugins = config.key('algorithms')
    log_lines = []
    entities = []
    try:
        for algo in data.algo_list:
            if algo.id not in plugins:
                raise RuntimeError("Method not available")
            definition = plugins[algo.id]
            for p in definition['params']:
                if p not in algo.params:
                    raise RuntimeError(f"Required parameter {p} not provided")
            parse = parse_get(algo.id)
            result, log = parse(data.text, algo.params)
            entities.extend(result)
            log_lines = log_lines + log

        return {
            '_v': API_VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'entities': json.dumps(entities),
            'log': json.dumps({'lines': log_lines}),
        }

    except Exception as e:
        logger.exception(e)
        return {
            '_v': API_VERSION,
            '_timestamp': datetime.now(pytz.utc),
            'entities': '[]',
            'log': json.dumps({'error': f"Error occured: {str(e)}"}),
        }
