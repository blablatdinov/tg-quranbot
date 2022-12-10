
from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

from app_types.stringable import ThroughStringable
from integrations.tg.message_id import MessageId


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
    (lazy_fixture('stringable_update'), 22628),
    (lazy_fixture('stringable_callback_update'), 22627),
])
def test(input_, expected):
    message_id = MessageId(input_)

    assert int(message_id) == expected
