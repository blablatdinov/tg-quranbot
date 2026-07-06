# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

import pytest
import pytz
from pytest_lazy_fixtures import lf

from app_types.fk_string import FkString
from integrations.tg.tg_datetime import TgDateTime
from integrations.tg.update import TgUpdate


@pytest.fixture
def message_update(message_update_factory):
    return FkString(message_update_factory())


@pytest.fixture
def stringable_callback_update(callback_update_factory):
    return callback_update_factory()


@pytest.mark.parametrize(('update', 'expected'), [
    (
        lf('message_update'),
        datetime.datetime(2022, 12, 9, 10, 20, 13, tzinfo=pytz.timezone('UTC')),
    ),
    (
        lf('stringable_callback_update'),
        datetime.datetime(2022, 10, 30, 15, 54, 34, tzinfo=pytz.timezone('UTC')),
    ),
])
def test(update, expected):
    tg_datetime = TgDateTime(TgUpdate.str_ctor(update))

    assert tg_datetime.datetime() == expected
