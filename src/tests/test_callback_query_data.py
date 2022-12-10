from pathlib import Path

import pytest

from app_types.stringable import ThroughStringable
from integrations.tg.callback_query import CallbackQueryData


@pytest.fixture()
def stringable_callback_update():
    return ThroughStringable(
        (Path(__file__).parent / 'fixtures' / 'button_callback.json').read_text(),
    )


def test(stringable_callback_update):
    cb_query_data = CallbackQueryData(stringable_callback_update)

    assert str(cb_query_data) == 'mark_readed(2362)'
