from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

from app_types.stringable import ThroughStringable
from integrations.tg.update_id import UpdateId


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
    (lazy_fixture('stringable_update'), 637463103),
    (lazy_fixture('stringable_callback_update'), 637463104),
])
def test(input_, expected):
    update_id = UpdateId(input_)

    assert int(update_id) == expected
