# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from integrations.tg.fk_chat_id import ChatId
from srv.podcasts.changed_podcast_reaction import PODCAST_ID_LITERAL, USER_ID_LITERAL, ChangedPodcastReaction
from srv.podcasts.podcast_reactions import PodcastReactions


@final
@attrs.define(frozen=True)
class PgChangedPoodcastReaction(ChangedPodcastReaction):
    """Реакция на подкаст в БД postgres."""

    _pgsql: AsyncEngine
    _chat_id: ChatId
    _reaction: PodcastReactions

    @override
    async def apply(self) -> None:
        """Применить."""
        query = '\n'.join([
            'SELECT reaction',
            'FROM podcast_reactions',
            'WHERE user_id = :user_id AND podcast_id = :podcast_id',
        ])
        async with self._pgsql.connect() as conn:
            result = await conn.execute(text(query), {
                USER_ID_LITERAL: int(self._chat_id),
                PODCAST_ID_LITERAL: self._reaction.podcast_id(),
            })
            row = result.fetchone()
        prayer_existed_reaction = row[0] if row else None
        if prayer_existed_reaction:
            if prayer_existed_reaction == self._reaction.status():
                query = '\n'.join([
                    'UPDATE podcast_reactions',
                    "SET reaction = 'showed'",
                    'WHERE user_id = :user_id AND podcast_id = :podcast_id',
                ])
                async with self._pgsql.connect() as conn:
                    await conn.execute(text(query), {
                        USER_ID_LITERAL: int(self._chat_id),
                        PODCAST_ID_LITERAL: self._reaction.podcast_id(),
                    })
                    await conn.commit()
            else:
                query = '\n'.join([
                    'UPDATE podcast_reactions',
                    'SET reaction = :reaction',
                    'WHERE user_id = :user_id AND podcast_id = :podcast_id',
                ])
                async with self._pgsql.connect() as conn:
                    await conn.execute(text(query), {
                        'reaction': self._reaction.status(),
                        USER_ID_LITERAL: int(self._chat_id),
                        PODCAST_ID_LITERAL: self._reaction.podcast_id(),
                    })
                    await conn.commit()
        else:
            query = '\n'.join([
                'INSERT INTO podcast_reactions (podcast_id, user_id, reaction)',
                'VALUES (:podcast_id, :user_id, :reaction)',
            ])
            async with self._pgsql.connect() as conn:
                await conn.execute(text(query), {
                    PODCAST_ID_LITERAL: self._reaction.podcast_id(),
                    USER_ID_LITERAL: int(self._chat_id),
                    'reaction': self._reaction.status(),
                })
                await conn.commit()
