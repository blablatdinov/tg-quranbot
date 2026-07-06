# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
from pytest_lazy_fixtures import lf

from integrations.tg.tg_chat_id import TgChatId
from integrations.tg.update import TgUpdate


@pytest.fixture
def stringable_update(message_update_factory):
    return message_update_factory('', 358610865)


@pytest.fixture
def stringable_callback_update(callback_update_factory):
    return callback_update_factory(chat_id=358610865)


@pytest.fixture
def query_search_update(inline_query_update_factory):
    return inline_query_update_factory('adsfawef')


@pytest.mark.parametrize('update', [
    lf('stringable_update'),
    lf('stringable_callback_update'),
    lf('query_search_update'),
])
def test(update):
    chat_id = TgChatId(TgUpdate.str_ctor(update))

    assert int(chat_id) == 358610865
