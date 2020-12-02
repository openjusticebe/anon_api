import logging
from time import sleep
from multiprocessing import Process
import uvicorn
from behave import fixture
from anon_api import main

PORT = 5555
HOST = '127.0.0.1'


def run_server():
    uvicorn.run(main.app, port=PORT, host=HOST)


@fixture
def server_api(_context, **_kwargs):
    proc = Process(target=run_server, args=(), daemon=True)
    logging.info('Starting server subprocess')
    proc.start()
    sleep(1.0)
    yield
    logging.info('Stopping server subprocess')
    proc.kill()
