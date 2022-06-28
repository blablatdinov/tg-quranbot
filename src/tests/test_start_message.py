import pytest

from services.start_message import StartMessageMeta, get_start_message_query


@pytest.mark.parametrize('input_,expected', [
    ('/start 89238', StartMessageMeta(referrer=89238)),
    ('/start 834ruiou', StartMessageMeta(referrer=None)),
    ('/start {"referrer": 28934}', StartMessageMeta(referrer=28934)),
    ('/start', StartMessageMeta(referrer=None)),
    ('/start {"some_param": "value"}', StartMessageMeta(referrer=None)),
    ('/start {"referrer":28934}', StartMessageMeta(referrer=28934)),
    ('/start {"referrer":"28934iwe"}', StartMessageMeta(referrer=None)),
])
def test(input_, expected):
    got = get_start_message_query(input_)

    assert got == expected
