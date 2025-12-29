# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.users.redis_user_state import RedisUserState


@final
@attrs.define(frozen=True)
class StepAnswer(TgAnswer):
    """Роутинг ответа по состоянию пользователя."""

    _step: str
    _origin: TgAnswer
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        step = await RedisUserState(self._redis, TgChatId(update), self._logger).step()
        if step.value != self._step:
            return []
        return await self._origin.build(update)
