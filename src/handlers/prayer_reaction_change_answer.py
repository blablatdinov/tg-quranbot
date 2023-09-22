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
from typing import Literal, final

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
from integrations.tg.tg_answers.audio_answer import TgAudioAnswer
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from services.reset_state_answer import ResetStateAnswer
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer
from srv.podcasts.podcast import RandomPodcast
from srv.podcasts.podcast_keyboard import PodcastKeyboard


@final
@attrs.define(frozen=True)
@elegant
class PrayerReaction(object):
    """Реакция на подкаст."""

    _callback_query: SupportsStr

    def podcast_id(self) -> int:
        """Идентификатор подкаста.

        :return: int
        """
        return int(re.findall(r'\((.+)\)', str(self._callback_query))[0])

    def status(self) -> Literal['like'] | Literal['dislike']:
        """Реакция.

        :return: Literal['like'] | Literal['dislike']
        """
        if 'dislike' in str(self._callback_query):
            return 'dislike'
        return 'like'


@final
@attrs.define(frozen=True)
@elegant
class PrayerReactionChangeAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _origin: TgAnswer
    _redis: Redis
    _pgsql: Database

    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: AnswerInterface
        """
        reaction = PrayerReaction(CallbackQueryData(update))
        query = """
            INSERT INTO podcast_reactions (podcast_id, user_id, reaction)
            VALUES (:podcast_id, :user_id, :reaction)
        """
        await self._pgsql.execute(query, {
            'podcast_id': reaction.podcast_id(),
            'user_id': int(TgChatId(update)),
            'reaction': reaction.status(),
        })
        podcast = RandomPodcast(
            SyncToAsyncIntable(reaction.podcast_id()),
            self._pgsql,
        )
        chat_id = int(TgChatId(update))
        return await ResetStateAnswer(
            TgAnswerMarkup(
                FileAnswer(
                    self._debug_mode,
                    TelegramFileIdAnswer(
                        TgChatIdAnswer(
                            TgAudioAnswer(
                                self._origin,
                            ),
                            chat_id,
                        ),
                        podcast,
                    ),
                    TgTextAnswer.str_ctor(
                        TgChatIdAnswer(
                            TgMessageAnswer(
                                self._origin,
                            ),
                            chat_id,
                        ),
                        await podcast.file_link(),
                    ),
                ),
                PodcastKeyboard(self._pgsql, podcast),
            ),
            self._redis,
        ).build(update)
