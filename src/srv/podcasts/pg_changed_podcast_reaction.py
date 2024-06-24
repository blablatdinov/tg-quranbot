from typing import final

import attrs
from databases import Database
from pyeo import elegant

from integrations.tg.chat_id import ChatId
from srv.podcasts.changed_podcast_reaction import PODCAST_ID_LITERAL, USER_ID_LITERAL, ChangedPodcastReaction
from srv.podcasts.podcast_reaction import PodcastReactions


@final
@attrs.define(frozen=True)
@elegant
class PgChangedPoodcastReaction(ChangedPodcastReaction):
    """Реакция на подкаст в БД postgres."""

    _pgsql: Database
    _chat_id: ChatId
    _reaction: PodcastReactions

    async def apply(self) -> None:
        """Применить."""
        query = '\n'.join([
            'SELECT reaction',
            'FROM podcast_reactions',
            'WHERE user_id = :user_id AND podcast_id = :podcast_id',
        ])
        prayer_existed_reaction = await self._pgsql.fetch_val(query, {
            USER_ID_LITERAL: int(self._chat_id),
            PODCAST_ID_LITERAL: self._reaction.podcast_id(),
        })
        if prayer_existed_reaction:
            if prayer_existed_reaction == self._reaction.status():
                query = '\n'.join([
                    'UPDATE podcast_reactions',
                    "SET reaction = 'showed'",
                    'WHERE user_id = :user_id AND podcast_id = :podcast_id',
                ])
                await self._pgsql.execute(query, {
                    USER_ID_LITERAL: int(self._chat_id),
                    PODCAST_ID_LITERAL: self._reaction.podcast_id(),
                })
            else:
                query = '\n'.join([
                    'UPDATE podcast_reactions',
                    'SET reaction = :reaction',
                    'WHERE user_id = :user_id AND podcast_id = :podcast_id',
                ])
                await self._pgsql.execute(query, {
                    'reaction': self._reaction.status(),
                    USER_ID_LITERAL: int(self._chat_id),
                    PODCAST_ID_LITERAL: self._reaction.podcast_id(),
                })
        else:
            query = '\n'.join([
                'INSERT INTO podcast_reactions (podcast_id, user_id, reaction)',
                'VALUES (:podcast_id, :user_id, :reaction)',
            ])
            await self._pgsql.execute(query, {
                PODCAST_ID_LITERAL: self._reaction.podcast_id(),
                USER_ID_LITERAL: int(self._chat_id),
                'reaction': self._reaction.status(),
            })