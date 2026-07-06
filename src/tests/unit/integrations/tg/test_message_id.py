# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
from pytest_lazy_fixtures import lf

from app_types.fk_string import FkString
from integrations.tg.message_id import TgMessageId
from integrations.tg.update import TgUpdate


@pytest.fixture
def stringable_update(message_update_factory):
    return FkString(message_update_factory())


@pytest.fixture
def stringable_callback_update(callback_update_factory):
    return callback_update_factory()


@pytest.mark.parametrize(('update', 'expected'), [
    (lf('stringable_update'), 22628),
    (lf('stringable_callback_update'), 22627),
])
def test(update, expected):
    message_id = TgMessageId(TgUpdate.str_ctor(update))

    assert int(message_id) == expected
