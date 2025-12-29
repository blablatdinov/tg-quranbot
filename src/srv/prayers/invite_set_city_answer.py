# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup
from integrations.tg.tg_chat_id import TgChatId
from services.switch_inline_query_answer import SwitchInlineQueryKeyboard
from srv.users.redis_user_state import RedisUserState
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
class InviteSetCityAnswer(TgAnswer):
    """Ответ с приглашением ввести город."""

    _message_answer: TgAnswer
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        await RedisUserState(
            self._redis, TgChatId(update), self._logger,
        ).change_step(UserStep.city_search)
        return await TgAnswerMarkup(
            self._message_answer,
            SwitchInlineQueryKeyboard(),
        ).build(update)
