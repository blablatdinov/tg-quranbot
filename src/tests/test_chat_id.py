from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

from app_types.stringable import ThroughStringable
from integrations.tg.chat_id import TgChatId


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


@pytest.mark.parametrize('input_', [
    lazy_fixture('stringable_update'),
    lazy_fixture('stringable_callback_update'),
])
def test(input_):
    chat_id = TgChatId(input_)

    assert int(chat_id) == 358610865
