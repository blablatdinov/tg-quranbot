"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re
from typing import Final, Literal, Protocol, final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.intable import SyncToAsyncIntable
from app_types.stringable import SupportsStr
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.message_id import TgMessageId
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerToSender, TgKeyboardEditAnswer, TgMessageIdAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from services.reset_state_answer import ResetStateAnswer
from services.user_state import CachedUserState, RedisUserState
from srv.podcasts.podcast import PgPodcast, Podcast
from srv.podcasts.podcast_answer import MarkuppedPodcastAnswer, PodcastAnswer
from srv.podcasts.podcast_keyboard import PodcastKeyboard

PODCAST_ID_LITERAL: Final = 'podcast_id'
USER_ID_LITERAL: Final = 'user_id'


@elegant
class PodcastReactionsT(Protocol):
    """Реакция на подкаст."""

    def podcast_id(self) -> int:
        """Идентификатор подкаста."""

    def status(self) -> Literal['like', 'dislike']:
        """Реакция."""


@final
@attrs.define(frozen=True)
@elegant
class PodcastReaction(PodcastReactionsT):
    """Реакция на подкастa.

    >>> prayer_reaction = PodcastReaction('like(17)')
    >>> prayer_reaction.podcast_id()
    17
    >>> prayer_reaction.status()
    'like'
    """

    _callback_query: SupportsStr

    @override
    def podcast_id(self) -> int:
        """Идентификатор подкаста.

        :return: int
        """
        return int(re.findall(r'\((.+)\)', str(self._callback_query))[0])

    @override
    def status(self) -> Literal['like', 'dislike']:
        """Реакция.

        :return: Literal['like', 'dislike']
        """
        if 'dislike' in str(self._callback_query):
            return 'dislike'
        return 'like'


async def _process(update, pgsql, reaction) -> Podcast:
    query = """
        SELECT reaction
        FROM podcast_reactions
        WHERE user_id = :user_id AND podcast_id = :podcast_id
    """
    chat_id = TgChatId(update)
    prayer_existed_reaction = await pgsql.fetch_val(query, {
        USER_ID_LITERAL: chat_id,
        PODCAST_ID_LITERAL: reaction.podcast_id(),
    })
    if prayer_existed_reaction:
        if prayer_existed_reaction == reaction.status():
            query = """
                DELETE FROM podcast_reactions
                WHERE user_id = :user_id AND podcast_id = :podcast_id
            """
            await pgsql.execute(query, {
                USER_ID_LITERAL: chat_id,
                PODCAST_ID_LITERAL: reaction.podcast_id(),
            })
        else:
            query = """
                UPDATE podcast_reactions
                SET reaction = :reaction
                WHERE user_id = :user_id AND podcast_id = :podcast_id
            """
            await pgsql.execute(query, {
                'reaction': reaction.status(),
                USER_ID_LITERAL: chat_id,
                PODCAST_ID_LITERAL: reaction.podcast_id(),
            })
    else:
        query = """
            INSERT INTO podcast_reactions (podcast_id, user_id, reaction)
            VALUES (:podcast_id, :user_id, :reaction)
        """
        await pgsql.execute(query, {
            PODCAST_ID_LITERAL: reaction.podcast_id(),
            USER_ID_LITERAL: chat_id,
            'reaction': reaction.status(),
        })
    return PgPodcast(
        SyncToAsyncIntable(reaction.podcast_id()),
        pgsql,
    )


@final
@attrs.define(frozen=True)
@elegant
class PodcastReactionChangeAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _origin: TgAnswer
    _redis: Redis
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: AnswerInterface
        """
        reaction = PodcastReaction(CallbackQueryData(update))
        podcast = await _process(update, self._pgsql, reaction)
        try:
            message_text = str(MessageText(update))
            origin: TgAnswer = TgMessageIdAnswer(
                TgKeyboardEditAnswer(
                    TgAnswerMarkup(
                        self._origin,
                        PodcastKeyboard(self._pgsql, podcast),
                    ),
                ),
                TgMessageId(update),
            )
        except MessageTextNotFoundError:
            print(reaction.podcast_id())
            origin: TgAnswer = PodcastAnswer(  # type: ignore [no-redef]
                self._origin,
                MarkuppedPodcastAnswer(
                    self._debug_mode,
                    self._origin,
                    self._redis,
                    self._pgsql,
                    podcast,
                ),
                self._redis,
                podcast,
                show_podcast_id=True,
            )
        return await ResetStateAnswer(
            TgAnswerToSender(origin),
            CachedUserState(RedisUserState(self._redis, TgChatId(update))),
        ).build(update)
