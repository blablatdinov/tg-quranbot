# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import re
from typing import final, override

import attrs
import httpx

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_chat_id import TgChatId


@final
@attrs.define(frozen=True)
class TgChatIdRegexAnswer(TgAnswer, SupportsStr):
    """Маршрутизация ответов по регулярному выражению в идентификаторе пользователя."""

    _pattern: str
    _answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        if 'callback_query' in str(update):
            return []
        try:
            regex_result = re.search(self._pattern, str(int(TgChatId(update))))
        except (AttributeError, MessageTextNotFoundError):
            return []
        if not regex_result:
            return []
        return await self._answer.build(update)

    @override
    def __str__(self) -> str:
        """Строковое представление.

        :return: str
        """
        return 'TgChatIdRegexAnswer. pattern: {0}'.format(self._pattern)
