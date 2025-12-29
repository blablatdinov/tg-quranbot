# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import re
from typing import final, override

import attrs
import httpx

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgMessageRegexAnswer(TgAnswer, SupportsStr):
    """Маршрутизация ответов по регулярному выражению."""

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
            regex_result = re.search(self._pattern, str(MessageText(update)))
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
        return 'TgMessageRegexAnswer. pattern: {0}'.format(self._pattern)
