import datetime
from pathlib import Path

import pytest
import pytz
from pytest_lazyfixture import lazy_fixture

from app_types.stringable import ThroughStringable
from integrations.tg.tg_datetime import TgDateTime


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
    (
        lazy_fixture('stringable_update'),
        datetime.datetime(2022, 12, 9, 10, 20, 13, tzinfo=pytz.timezone('UTC')),
    ),
    (
        lazy_fixture('stringable_callback_update'),
        datetime.datetime(2022, 10, 30, 15, 54, 34, tzinfo=pytz.timezone('UTC')),
    ),
])
def test(input_, expected):
    tg_datetime = TgDateTime(input_)

    assert tg_datetime.datetime() == expected
