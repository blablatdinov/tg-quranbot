from app_types.update import Update
from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer


import attrs
import httpx
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class CityNotSupportedAnswer(TgAnswer):
    """Ответ о неподдерживаемом городе."""

    _origin: TgAnswer
    _error_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except CityNotSupportedError:
            return await TgTextAnswer.str_ctor(
                self._error_answer,
                'Этот город не поддерживается',
            ).build(update)