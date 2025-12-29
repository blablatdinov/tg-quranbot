# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.favorites_answer import FavoriteAyatsAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test_favorite_ayats_answer(pgsql, fake_redis):
    debug = False
    got = await FavoriteAyatsAnswer(debug, pgsql, fake_redis, FkAnswer(), FkLogSink()).build(
        FkUpdate(ujson.dumps({
            'chat': {'id': 74359},
        })),
    )

    assert got[0].url.params['text'] == 'Вы еще не добавляли аятов в избранное'
