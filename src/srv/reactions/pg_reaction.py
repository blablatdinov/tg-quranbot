# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
from typing import Final, Protocol, final

import attrs
from databases import Database
from pyeo import elegant

from integrations.tg.chat_id import ChatId
from srv.reactions.podcast_reaction import PodcastReactionsT

PODCAST_ID_LITERAL: Final = 'podcast_id'
USER_ID_LITERAL: Final = 'user_id'


@elegant
class Reaction(Protocol):
    """Реакция на подкаст."""

    async def apply(self) -> None:
        """Применить."""


@final
@attrs.define(frozen=True)
@elegant
class PgReaction(Reaction):
    """Реакция на подкаст в БД postgres."""

    _pgsql: Database
    _chat_id: ChatId
    _reaction: PodcastReactionsT

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
