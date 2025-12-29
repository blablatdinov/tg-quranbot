# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.paginate_by_search_ayat import PaginateBySearchAyat
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test(fake_redis, pgsql, settings_ctor):
    got = await PaginateBySearchAyat(
        FkAnswer(),
        fake_redis,
        pgsql,
        settings_ctor(),
        FkLogSink(),
    ).build(FkUpdate(ujson.dumps({
        'chat': {'id': 843759},
        'callback_query': {
            'data': '1',
        },
    })))

    assert got[0].url.params['text'] == 'Пожалуйста, введите запрос для поиска:'
