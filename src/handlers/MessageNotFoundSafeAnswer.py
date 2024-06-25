from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.tg_answers import TgAnswer


import attrs
import httpx
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class MessageNotFoundSafeAnswer(TgAnswer):

    _origin: TgAnswer
    _new_message_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        try:
            return await self._origin.build(update)
        except MessageTextNotFoundError:
            return await self._new_message_answer.build(update)