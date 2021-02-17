from fastapi import APIRouter, status, File, UploadFile
from datetime import datetime
import asyncio
import uuid
import requests
from ..lib_cfg import (config)
from ..lib_misc import (
    DocParse,
)
from ..deps import (
    # config,
    logger,
    QUEUES,
)

router = APIRouter()


# ##################################### ROUTES
# ############################################
@router.post('/extract/', tags=['extract'])
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


@router.get('/extract/status', tags=['extract'])
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
            if delta < config.key('ttl_result_seconds'):
                # Filter TTL's
                logger.info('Putting msg back in queue %s', msg.ref)
                QUEUES["parseOut"].put_nowait(msg)


@router.post('/fileinfo/', tags=['extract'])
async def fileinfo(rawFile: UploadFile = File(...)):
    """
    Get info about file
    """
    tConf = config.key('tika')
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
