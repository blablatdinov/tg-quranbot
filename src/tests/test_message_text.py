from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

from app_types.stringable import ThroughStringable
from integrations.tg.message_text import MessageText


@pytest.fixture()
def stringable_update():
    return ThroughStringable(
        (Path(__file__).parent / 'fixtures' / 'message_update.json').read_text(),
    )


@pytest.fixture()
def stringable_callback_update():
    return ThroughStringable(
        (Path(__file__).parent / 'fixtures' / 'button_callback.json').read_text(),
    )


@pytest.mark.parametrize('input_,expected', [
    (lazy_fixture('stringable_update'), 'afwe'),
    (lazy_fixture('stringable_callback_update'), 'awef'),
    ('{"text":"hello"}', 'hello'),
])
def test(input_, expected):
    got = MessageText(input_)

    assert str(got) == expected
