# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.intable import AsyncInt
from integrations.tg.fk_chat_id import ChatId


@final
@attrs.define(frozen=True)
class PodcastId(AsyncInt):
    """Идентификатор подкаста.

    Достаем случайный идентификатор подкаста, который пользователю еще не попадался
    """

    _pgsql: AsyncEngine
    _chat_id: ChatId

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        query = '\n'.join([
            'SELECT p.podcast_id',
            'FROM podcasts AS p',
            'LEFT JOIN podcast_reactions AS pr ON pr.podcast_id = p.podcast_id',
            'WHERE p.podcast_id NOT IN (',
            '    SELECT podcast_id',
            '    FROM podcast_reactions ',
            '    WHERE user_id = :chat_id',
            ')',
            'ORDER BY RANDOM()',
        ])
        async with self._pgsql.connect() as conn:
            podcast_id = (await conn.execute(
                text(query),
                {'chat_id': int(self._chat_id)},
            )).scalar()
            if not podcast_id:
                return (await conn.execute(text('SELECT podcast_id FROM podcasts ORDER BY RANDOM()'))).scalar()
            await conn.execute(
                text('\n'.join([
                    'INSERT INTO podcast_reactions (podcast_id, user_id, reaction)',
                    'VALUES (:podcast_id, :user_id, :reaction)',
                ])),
                {'podcast_id': podcast_id, 'user_id': int(self._chat_id), 'reaction': 'showed'},
            )
            return podcast_id
