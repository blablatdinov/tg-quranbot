# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.callback_query import CallbackQueryData


def test(callback_update_factory):
    cb_query_data = CallbackQueryData(FkUpdate(callback_update_factory(callback_data='mark_readed(2362)')))

    assert str(cb_query_data) == 'mark_readed(2362)'
