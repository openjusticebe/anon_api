import json
import logging
from datetime import datetime

import httpx
import websockets

from anon_api.lib_misc import DocResult

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())


async def doc_parser(config, queue_in, queue_ocr, queue_out):
    """
    This worker reads file metadata (and content if available) from the TIKA endpoint.
    It does not do OCR : it only pushes the doc to be OCR'd on the OCR queue if necessary.

    Roles:
        - get document metadata
        - get document text if text available
        - push document to OCR work queue
    """
    while True:
        doc = await queue_in.get()
        logger.debug('Parser job received for %s', doc.ref)
        delta = (datetime.now() - doc.ttl).total_seconds()
        if delta > config.key('ttl_parse_seconds'):
            logger.warning('Parse TTL expired for %s', doc.ref)
            queue_out.put_nowait(DocResult(doc.ref, 'error', 'parse_ttl_expired', datetime.now()))
            continue

        # Get Meta Data
        tConf = config.key('tika')
        tika_server = f"http://{tConf['host']}:{tConf['port']}/rmeta/form/text"
        try:
            async with httpx.AsyncClient() as client:
                doc.file.file.seek(0)
                raw = await client.post(
                    tika_server,
                    files={'upload': doc.file.file.read()},
                    headers={'Accept': 'application/json'},
                    timeout=30,
                )
                rawResp = raw.json()
                resp = rawResp[0]
                chars = [int(v) for v in resp.get('pdf:charsPerPage', [])]

                langCheck = resp.get('language', None) is not None
                charCheck = sum(chars) > len(chars)
                doOcr = not (langCheck or charCheck)

                data = {
                    "language": resp.get('language', None),
                    "charsperpage": chars,
                    "charstotal": sum(chars),
                    "pages": len(chars),
                    "doOcr": doOcr,
                    "filename": doc.file.filename,
                    "content_type": doc.file.content_type,
                    "size_bytes": doc.file.file.tell(),
                }

            queue_out.put_nowait(DocResult(doc.ref, 'meta', data, datetime.now()))

            if doOcr:
                # Add doc to the OCR Queue
                queue_ocr.put_nowait(doc)
            else:
                # No OCR to be done, just push already obtained text data
                queue_out.put_nowait(DocResult(
                    doc.ref,
                    'text',
                    resp.get('X-TIKA:content').strip(),
                    datetime.now()
                ))

        except httpx.ReadTimeout:
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'Timeout occured ! Document too big ? :(',
                datetime.now()
            ))
        except httpx.NetworkError:
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'Server is gone fishing!',
                datetime.now()
            ))
        except Exception as e:
            logger.critical('!!!!! PARSE TASK FAILED !!!! (what happened ?)')
            logger.exception(e)
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'Unexpected exception occured - sorry !',
                datetime.now()
            ))
        finally:
            queue_in.task_done()


async def tika_ocr(config, queue_in, queue_out):
    tConf = config.key('tika_ocr')
    tika_server = f"http://{tConf['host']}:{tConf['port']}/tika/form"
    while True:
        doc = await queue_in.get()
        logger.debug('Tika OCR job received for %s', doc.ref)
        delta = (datetime.now() - doc.ttl).total_seconds()
        if delta > config.key('ttl_parse_seconds'):
            logger.warning('OCR TTL expired for %s', doc.ref)
            queue_out.put_nowait(DocResult(doc.ref, 'error', 'parse_ttl_expired', datetime.now()))
            continue

        try:
            async with httpx.AsyncClient() as client:
                doc.file.file.seek(0)
                raw = await client.post(
                    tika_server,
                    files={'upload': doc.file.file.read()},
                    headers={'Accept': 'text/plain; charset=UTF-8'},
                    timeout=120,
                )
                if raw.status_code != 200:
                    queue_out.put_nowait(DocResult(
                        doc.ref,
                        'error',
                        'extraction_server_error',
                        datetime.now()
                    ))
                    continue

            queue_out.put_nowait(DocResult(
                doc.ref,
                'text',
                raw.text,
                datetime.now()
            ))
        except httpx.ReadTimeout:
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'Bad news : Tika Timeout occured ! Document too big ? :(',
                datetime.now()
            ))
        except Exception as e:
            logger.critical('!!!!! TIKA OCR TASK FAILED !!!! (check tika connection)')
            logger.exception(e)
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'exception occured: internal error',
                datetime.now()
            ))
        finally:
            queue_in.task_done()


async def pyghotess_ocr(config, queue_in, queue_out):
    """
    Send the file to the pyghotess endpoint (only websocket implemented at this point)
    and wait for the results to come in, pushing them directly to the output queue
    """

    conf = config.key('pyghotess')
    uri = f"ws://{conf['host']}:{conf['port']}/ws"
    logger.info('Websocket uri defined as :%s', uri)

    while True:
        doc = await queue_in.get()
        logger.debug('Pyghotess OCR job received for %s', doc.ref)
        delta = (datetime.now() - doc.ttl).total_seconds()
        if delta > config.key('ttl_parse_seconds'):
            logger.warning('OCR TTL expired for %s', doc.ref)
            queue_out.put_nowait(DocResult(doc.ref, 'error', 'parse_ttl_expired', datetime.now()))
            continue

        try:
            async with websockets.connect(uri) as ws:
                # Send file to websocket
                await ws.send(json.dumps({
                    'action': 'upload',
                    'filename': doc.ref
                }))
                resp = await ws.recv()
                logger.debug('Upload check : %s', resp)
                logger.info('Upload request sent')

                # Make sure we're at the start of the file
                doc.file.file.seek(0)
                i = 1
                while chunk := doc.file.file.read(1024 * 1024):
                    logger.debug('Sending file chunk %s', i)
                    i += 1
                    await ws.send(chunk)

                # Send empty byte array to signal end of file
                await ws.send(bytearray())
                logger.debug('File %s sent', doc.ref)

                # Wait for OCR results
                async for message in ws:
                    result = json.loads(message)
                    logger.debug('WS message received: %s', result['action'])
                    if result['action'] == 'done':
                        break
                    if result['action'] == 'page_extract':
                        payload = {
                            'page': result['meta']['page'],
                            'text': result['payload']
                        }
                        queue_out.put_nowait(DocResult(
                            doc.ref,
                            'page',
                            payload,
                            datetime.now()
                        ))

        except websockets.ConnectionClosedOK:
            logger.info('Connection closed')
        except websockets.ConnectionClosedError:
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'Bad news : Connection closed unexpectedly',
                datetime.now()
            ))
        except Exception as e:
            logger.critical('!!!!! PYTHOTESS OCR TASK FAILED !!!! (check server logs)')
            logger.exception(e)
            queue_out.put_nowait(DocResult(
                doc.ref,
                'error',
                'exception occured: internal error',
                datetime.now()
            ))
        finally:
            logger.info('Pyghotess ocr done')
            queue_in.task_done()
