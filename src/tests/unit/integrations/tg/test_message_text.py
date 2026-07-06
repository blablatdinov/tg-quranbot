# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
from pytest_lazy_fixtures import lf

from app_types.fk_string import FkString
from integrations.tg.message_text import MessageText
from integrations.tg.update import TgUpdate


@pytest.fixture
def stringable_update(message_update_factory):
    return FkString(message_update_factory('afwe'))


@pytest.fixture
def stringable_callback_update(callback_update_factory):
    return callback_update_factory()


@pytest.mark.parametrize(('update', 'expected'), [
    (lf('stringable_update'), 'afwe'),
    (lf('stringable_callback_update'), 'awef'),
    ('{"message":{"text":"hello"}}', 'hello'),
])
def test(update, expected):
    got = MessageText(TgUpdate.str_ctor(update))

    assert str(got) == expected
