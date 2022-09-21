import re

import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgCallbackQueryRegexAnswer(TgAnswerInterface):
    """Маршрутизация ответов по регулярному выражению."""

    def __init__(self, pattern: str, answer: TgAnswerInterface):
        self._pattern = pattern
        self._answer = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            regex_result = re.search(self._pattern, update.callback_query.data)
        except AttributeError:
            return []
        if not regex_result:
            return []
        return await self._answer.build(update)
