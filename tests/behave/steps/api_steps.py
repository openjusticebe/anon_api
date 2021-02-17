import requests
import json
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


@given(u'some example text')
def step_impl(context):
    context.txt = """
Robert serait le fils d'Erlebert et le neveu de Robert, référendaire de Dagobert Ier.
Il est connu dès 654 à la cour de Clovis II et l'historienne Ingrid Heidrich le dit maire du palais de Neustrie en 654, mais son avis n'est pas partagé, car la charge était alors tenue par Erchinoald.

Il accéda ensuite aux charges de comte palatin puis de chancelier de Clotaire III, roi des Francs en Neustrie.

Partisan d'Ébroïn, il fit exécuter sur son ordre et contre son gré saint Léger le 2 octobre 6776 (ou 6771, ou 6797).

Il meurt peu après puisqu'un acte du 12 septembre 678, mentionne que sa veuve Théoda a hérité de ses biens, la veuve étant également décédée à la date de l'acte. Théoda serait un diminutif de Théodrade, et comme son fils Lambert fut placé sous la protection Théodard de Maastricht, évêque de Tongres et qu'il lui succède ensuite comme évêque, Christian Settipani propose de la voir comme une sœur de Théodard

Il serait le grand-père de Lambert de Hesbaye et donc probablement un membre de la famille des Robertiens et un ancêtre direct des Capétiens.
"""


@when(u'I send text file for pseudonymisation')
def step_impl(context):
    payload = {
        "_v": 1,
        "_timestamp": 1239120938,
        "algo_list": [{
            "id": "anon_trazor",
            "params": "{}"
        }],
        "format": "text",
        "encoding": "utf8",
        "text": context.txt
    }
    r = requests.post(
        f'http://{context.api_host}:{context.api_port}/run',
        json=payload
    )
    assert r.status_code == 200
    context.json = r.json()


@then(u'I receive a pseudonymised text')
def step_impl(context):
    parsed_text = context.json['text']
    print(parsed_text)
    assert('Robert' not in parsed_text)
    assert('Lambert' not in parsed_text)
