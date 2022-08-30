from typing import Optional

from aiogram import types


class AnswerInterface(object):
    """Интерфейс для отсылаемых объектов."""

    chat_id: Optional[int]

    async def send(self) -> list[types.Message]:
        """Метод для отправки ответа.

        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError
