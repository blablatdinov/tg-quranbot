# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from integrations.tg.inline_query import InlineQuery
from integrations.tg.update import TgUpdate


@pytest.fixture
def inline_query_update(inline_query_update_factory):
    return inline_query_update_factory('Search')


def test(inline_query_update):
    got = str(InlineQuery(TgUpdate.str_ctor(inline_query_update)))

    assert got == 'Search'
