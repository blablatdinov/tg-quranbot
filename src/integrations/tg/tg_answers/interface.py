from typing import Protocol

import httpx

from app_types.stringable import Stringable


class TgAnswerInterface(Protocol):
    """Интерфейс ответа пользователю."""

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        """


class FkAnswer(TgAnswerInterface):
    """Фейковый ответ."""

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [httpx.Request('GET', url='https://some.domain')]
