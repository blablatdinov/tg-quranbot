from typing import final, override

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
@elegant
class FkAnswer(TgAnswer):
    """Фейковый ответ."""

    _url: str | None = 'https://some.domain'

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        :raises ValueError: if self._url is None
        """
        if self._url is None:
            raise ValueError
        return [httpx.Request('GET', self._url)]
