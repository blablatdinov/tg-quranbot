from pathlib import Path

import pytest

from app_types.stringable import ThroughStringable
from integrations.tg.tg_answers import FkAnswer, TgMessageRegexAnswer


@pytest.fixture()
def callback_update():
    return (Path(__file__).parent / 'fixtures' / 'callback_update.json').read_text()


@pytest.fixture()
def message_update():
    return (Path(__file__).parent / 'fixtures' / 'message_update.json').read_text()


async def test_on_message_update(message_update):
    got = await TgMessageRegexAnswer(r'\d+:\d+', FkAnswer()).build(ThroughStringable(message_update))

    assert got


async def test_on_callback_update(callback_update):
    got = await TgMessageRegexAnswer(r'\d+:\d+', FkAnswer()).build(ThroughStringable(callback_update))

    assert not got
