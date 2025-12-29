# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery


@final
@attrs.define(frozen=True)
class CachedAyatSearchQueryAnswer(TgAnswer):
    """Объект кэширует запрос на поиск аятов, для использования в пагинации."""

    _origin: TgAnswer
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        await AyatTextSearchQuery(
            self._redis,
            TgChatId(update),
            self._logger,
        ).write(str(MessageText(update)))
        return await self._origin.build(update)
