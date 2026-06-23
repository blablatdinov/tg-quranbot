# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypedDict, final, override

import attrs
import ujson
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from srv.podcasts.podcast import Podcast


@final
class _Row(TypedDict):

    like_count: int
    dislike_count: int


@final
@attrs.define(frozen=True)
class PodcastKeyboard(Keyboard):
    """Клавиатура подкаста."""

    _pgsql: AsyncEngine
    _podcast: Podcast

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        query = '\n'.join([
            'SELECT',
            "    COUNT(CASE WHEN reaction = 'like' THEN 1 END) AS like_count,",
            "    COUNT(CASE WHEN reaction = 'dislike' THEN 1 END) AS dislike_count",
            'FROM podcast_reactions',
            'WHERE podcast_id = :podcast_id',
            'GROUP BY podcast_id',
        ])
        podcast_id = await self._podcast.podcast_id()
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {'podcast_id': podcast_id})
            row = query_result.mappings().fetchone()
        if row:
            likes_count_map = _Row(
                like_count=row['like_count'],
                dislike_count=row['dislike_count'],
            )
        else:
            likes_count_map = _Row(
                like_count=0,
                dislike_count=0,
            )
        return ujson.dumps({
            'inline_keyboard': [[
                {
                    'text': '👍 {0}'.format(likes_count_map['like_count']),
                    'callback_data': 'like({0})'.format(podcast_id),
                },
                {
                    'text': '👎 {0}'.format(likes_count_map['dislike_count']),
                    'callback_data': 'dislike({0})'.format(podcast_id),
                },
            ]],
        })it/handlers/test_next_day_ayats.py
