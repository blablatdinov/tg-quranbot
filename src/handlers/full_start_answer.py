# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgHtmlParseAnswer, TgMessageAnswer
from integrations.tg.tg_chat_id import TgChatId
from services.answers.default_keyboard import DefaultKeyboard
from services.answers.resized_keyboard import ResizedKeyboard
from services.reset_state_answer import ResetStateAnswer
from settings import Settings
from srv.admin_messages.pg_admin_message import PgAdminMessage
from srv.events.sink import Sink
from srv.start.new_tg_user import NewTgUser
from srv.start.start_answer import StartAnswer
from srv.start.user_already_active import UserAlreadyActiveSafeAnswer
from srv.start.user_already_exists import UserAlreadyExistsAnswer
from srv.users.cached_user_state import CachedUserState
from srv.users.redis_user_state import RedisUserState


@attrs.define(frozen=True)
@final
class FullStartAnswer(TgAnswer):
    """Ответ на команду /start."""

    _pgsql: Database
    _empty_answer: TgAnswer
    _event_sink: Sink
    _redis: Redis
    _settings: Settings
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await ResetStateAnswer(
            TgAnswerMarkup(
                UserAlreadyActiveSafeAnswer(
                    UserAlreadyExistsAnswer(
                        StartAnswer(
                            TgHtmlParseAnswer(
                                TgMessageAnswer(self._empty_answer),
                            ),
                            PgAdminMessage('start', self._pgsql),
                            NewTgUser(
                                self._pgsql,
                                self._logger,
                                self._event_sink,
                                update,
                            ),
                            self._pgsql,
                            self._settings.admin_chat_ids(),
                        ),
                        answer_to_sender,
                        self._pgsql,
                        self._event_sink,
                    ),
                    answer_to_sender,
                ),
                ResizedKeyboard(
                    DefaultKeyboard(),
                ),
            ),
            CachedUserState(RedisUserState(self._redis, TgChatId(update), self._logger)),
        ).build(update)
