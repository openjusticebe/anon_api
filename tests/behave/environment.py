# pylint: skip-file
from behave import use_fixture
from fixtures import server_api, PORT, HOST


# Fixture Settings
# ##################################################################
def before_tag(context, tag):
    if tag == 'fixture.api':
        use_fixture(server_api, context)
    pass


# Setup & Breakdown
# ##################################################################
def before_all(context):
    context.api_port = PORT
    context.api_host = HOST
    pass


def after_all(context):
    pass


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    pass

