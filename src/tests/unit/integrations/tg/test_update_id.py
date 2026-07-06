# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
from pytest_lazy_fixtures import lf

from integrations.tg.update import TgUpdate
from integrations.tg.update_id import UpdateId


@pytest.mark.parametrize(('update_factory', 'expected'), [
    (lf('message_update_factory'), 637463103),
    (lf('callback_update_factory'), 637463104),
])
def test(update_factory, expected):
    update_id = UpdateId(TgUpdate.str_ctor(update_factory()))

    assert int(update_id) == expected
