from typing import final, override

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
@elegant
class UserWithoutCitySafeAnswer(TgAnswer):
    """Объект для обработки случаев когда пользователь запрашивает время намаза без установленного города."""

    _origin: TgAnswer
    _invite_set_city_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserHasNotCityIdError:
            return await self._invite_set_city_answer.build(update)
