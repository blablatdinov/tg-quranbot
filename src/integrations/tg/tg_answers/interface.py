from typing import Protocol

import httpx

from app_types.stringable import Stringable


class TgAnswerInterface(Protocol):
    """Интерфейс ответа пользователю."""

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
