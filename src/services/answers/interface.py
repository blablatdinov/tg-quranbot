from typing import Optional, Union

from aiogram import types


class AnswerInterface(object):
    """Интерфейс для отсылаемых объектов."""

    chat_id: Optional[int]

    async def send(self) -> list[types.Message]:
        """Метод для отправки ответа.

        :param chat_id: int
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError
