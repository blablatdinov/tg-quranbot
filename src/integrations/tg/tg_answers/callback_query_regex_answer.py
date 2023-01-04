import re

import httpx

from app_types.stringable import Stringable
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgCallbackQueryRegexAnswer(TgAnswerInterface):
    """Маршрутизация ответов по регулярному выражению."""

    def __init__(self, pattern: str, answer: TgAnswerInterface):
        """Конструктор класса.

        :param pattern: str
        :param answer: TgAnswerInterface
        """
        self._pattern = pattern
        self._answer = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            regex_result = re.search(self._pattern, str(CallbackQueryData(update)))
        except AttributeError:
            return []
        if not regex_result:
            return []
        return await self._answer.build(update)
