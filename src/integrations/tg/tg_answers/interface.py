from typing import Protocol

import httpx

from integrations.tg.tg_answers.update import Update


class TgAnswerInterface(Protocol):
    """Интерфейс ответа пользователю."""

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
