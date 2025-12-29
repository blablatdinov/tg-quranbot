# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from integrations.tg.tg_chat_id import TgChatId
from services.reset_state_answer import ResetStateAnswer
from srv.admin_messages.admin_message import AdminMessage
from srv.users.cached_user_state import CachedUserState
from srv.users.redis_user_state import RedisUserState


@final
@attrs.define(frozen=True)
class HelpAnswer(TgAnswer):
    """Ответ на команду /help."""

    _origin: TgAnswer
    _admin_message: AdminMessage
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await ResetStateAnswer(
            TgTextAnswer(
                TgHtmlMessageAnswerToSender(self._origin),
                self._admin_message,
            ),
            CachedUserState(
                RedisUserState(self._redis, TgChatId(update), self._logger),
            ),
        ).build(update)
