from typing import Optional

from services.answers.answer import Answer


class AnswerInterface(object):
    """Интерфейс для отсылаемых объектов."""

    chat_id: Optional[int]

    async def send(self, chat_id: int = None):
        """Метод для отправки ответа.

        :param chat_id: int
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError

    def to_list(self) -> list['Answer']:
        """Метод для конвертации в список.

        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError
