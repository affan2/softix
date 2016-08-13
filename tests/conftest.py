import pytest
import softix
import mock
import betamax
import base64
import os
from betamax_matchers import json_body
from betamax_serializers import pretty_json

betamax.Betamax.register_request_matcher(json_body.JSONBodyMatcher)
credentials = [os.environ.get('CLIENT_ID', 'foo').encode(),
               os.environ.get('SECRET', 'foo').encode()]

@pytest.fixture(scope='module')
def softixcore():
    """
    Returns a softixcore instance

    For unit testing, we need to create mocks for the session
    """
    sc = softix.SoftixCore()
    sc.session = create_mocked_session()
    sc.build_url = build_url
    return sc

@pytest.fixture(scope='module')
def recorder():
    """
    Create a betamax instance.
    """
    return betamax.Betamax()



def build_url(*args, **kwargs):
    return softix.sessions.Session().build_url(*args, **kwargs)
    

def create_mocked_session():
    """
    Create a mocked session.
    """
    session_mock = mock.create_autospec(softix.sessions.Session)
    return session_mock

betamax.Betamax.register_request_matcher(json_body.JSONBodyMatcher)
betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['match_requests_on'].append('json-body')
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.define_cassette_placeholder(
        '<BASIC_AUTH>',
        base64.b64encode(b':'.join(credentials)).decode()
    )


