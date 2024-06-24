from app_types.update import Update
from exceptions.content_exceptions import TelegramFileIdNotFilledError
from integrations.tg.tg_answers import TgAnswer


import attrs
import httpx
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class TgFileIdNotFilledSafeAnswer(TgAnswer):
    """Декоратор для обработки файлов с незаполненным идентификатором файла."""

    _file_id_answer: TgAnswer
    _text_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._file_id_answer.build(update)
        except TelegramFileIdNotFilledError:
            return await self._text_answer.build(update)