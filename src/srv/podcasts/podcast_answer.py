# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers.answer_list import TgAnswerList
from integrations.tg.tg_answers.chat_id_answer import TgChatIdAnswer
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.skipable_answer import SkipableAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from services.reset_state_answer import ResetStateAnswer
from srv.podcasts.podcast import Podcast
from srv.users.cached_user_state import CachedUserState
from srv.users.redis_user_state import RedisUserState


@final
@attrs.define(frozen=True)
class PodcastAnswer(TgAnswer):
    """Ответ с подкастом."""

    _origin: TgAnswer
    _markupped_answer: TgAnswer
    _redis: Redis
    _podcast: Podcast
    _logger: LogSink
    _show_podcast_id: bool

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        chat_id = TgChatId(update)
        return await ResetStateAnswer(
            TgAnswerList.ctor(
                SkipableAnswer(
                    not self._show_podcast_id,
                    TgTextAnswer.str_ctor(
                        TgChatIdAnswer(
                            TgMessageAnswer(
                                self._origin,
                            ),
                            chat_id,
                        ),
                        '/podcast{0}'.format(await self._podcast.podcast_id()),
                    ),
                ),
                self._markupped_answer,
            ),
            CachedUserState(RedisUserState(self._redis, TgChatId(update), self._logger)),
        ).build(update)
