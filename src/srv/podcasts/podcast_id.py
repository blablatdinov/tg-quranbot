# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.intable import AsyncInt
from integrations.tg.fk_chat_id import ChatId


@final
@attrs.define(frozen=True)
class PodcastId(AsyncInt):
    """Идентификатор подкаста.

    Достаем случайный идентификатор подкаста, который пользователю еще не попадался
    """

    _pgsql: Database
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
        podcast_id = await self._pgsql.fetch_val(query, {'chat_id': int(self._chat_id)})
        if not podcast_id:
            return await self._pgsql.fetch_val('SELECT podcast_id FROM podcasts ORDER BY RANDOM()')
        await self._pgsql.execute(
            'INSERT INTO podcast_reactions (podcast_id, user_id, reaction) VALUES (:podcast_id, :user_id, :reaction)',
            {'podcast_id': podcast_id, 'user_id': int(self._chat_id), 'reaction': 'showed'},
        )
        return podcast_id
