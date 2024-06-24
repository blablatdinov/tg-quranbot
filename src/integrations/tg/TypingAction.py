from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer


import attrs
import httpx
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class TypingAction(TgAnswer):
    """Действие с печатью."""

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                method=request.method, url=request.url.copy_add_param('action', 'typing'), headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]