import requests
import os
from behave import when, given, then


@given(u'the api is available')
def step_impl(context):
    r = requests.get(f'http://{context.api_host}:{context.api_port}/')
    data = r.json()
    assert r.status_code == 200
    assert 'all_systems' in data
    assert data['all_systems'] == 'nominal'


@when(u'I access the server root')
def step_impl(context):
    r = requests.get(f'http://{context.api_host}:{context.api_port}/')
    context.json = r.json()


@then(u'I receive some data')
def step_impl(context):
    assert 'all_systems' in context.json
    assert context.json['all_systems'] == 'nominal'


@when(u'I send a pdf text file for extraction')
def step_impl(context):
    url = f'http://{context.api_host}:{context.api_port}/extract/'
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../../ressources/sample_text.pdf'
    )
    files = {'rawFile': open(path, 'rb')}
    r = requests.post(url, files=files)
    context.data = r.json()


@then(u'I receive a reference')
def step_impl(context):
    print(context.data)
    assert 'ref' in context.data
    context.ref = context.data['ref']


@when(u'I use the reference to check file status')
def step_impl(context):
    r = requests.get(
        f'http://{context.api_host}:{context.api_port}/extract/status?ref={context.ref}'
    )
    assert r.status_code == 200
    context.json = r.json()
    print(context.json)


@then(u'I receive some meta data')
def step_impl(context):
    assert context.json['ref'] == context.ref
    assert context.json['status'] == 'meta'
    assert isinstance(context.json['value']['filename'], str)


@given(u'I wait a bit')
def step_impl(context):
    import time
    time.sleep(4)


@then(u'I receive the extracted text')
def step_impl(context):
    assert context.json['ref'] == context.ref
    assert context.json['status'] == 'text'
    assert isinstance(context.json['value'], str)
