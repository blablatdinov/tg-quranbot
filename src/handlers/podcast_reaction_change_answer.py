# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.fk_async_int import FkAsyncInt
from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from handlers.podcast_message_text_not_exists_safe_answer import PodcastMessageTextNotExistsSafeAnswer
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import TgAnswerToSender, TgKeyboardEditAnswer, TgMessageIdAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_answers.tg_answer_markup import TgAnswerMarkup
from integrations.tg.tg_chat_id import TgChatId
from services.reset_state_answer import ResetStateAnswer
from srv.podcasts.markupped_podcast_answer import MarkuppedPodcastAnswer
from srv.podcasts.parsed_podcast_reaction import ParsedPodcastReaction
from srv.podcasts.pg_changed_podcast_reaction import PgChangedPoodcastReaction
from srv.podcasts.pg_podcast import PgPodcast
from srv.podcasts.podcast_answer import PodcastAnswer
from srv.podcasts.podcast_keyboard import PodcastKeyboard
from srv.users.cached_user_state import CachedUserState
from srv.users.redis_user_state import RedisUserState


@final
@attrs.define(frozen=True)
class PodcastReactionChangeAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _origin: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        reaction = ParsedPodcastReaction(CallbackQueryData(update))
        podcast = PgPodcast(
            FkAsyncInt(reaction.podcast_id()),
            self._pgsql,
        )
        await PgChangedPoodcastReaction(
            self._pgsql,
            TgChatId(update),
            reaction,
        ).apply()
        return await ResetStateAnswer(
            PodcastMessageTextNotExistsSafeAnswer(
                TgMessageIdAnswer(
                    TgAnswerToSender(
                        TgKeyboardEditAnswer(
                            TgAnswerMarkup(
                                self._origin,
                                PodcastKeyboard(self._pgsql, podcast),
                            ),
                        ),
                    ),
                    TgMessageId(update),
                ),
                PodcastAnswer(
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
                    self._logger,
                    show_podcast_id=True,
                ),
            ),
            CachedUserState(RedisUserState(self._redis, TgChatId(update), self._logger)),
        ).build(update)
