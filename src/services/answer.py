from typing import Optional

from pydantic import BaseModel

from utlls import get_bot_instance


class AnswerInterface(object):
    """Интерфейс для отсылаемых объектов."""

    async def send(self, chat_id: int = None):
        """Метод для отправки ответа.

        :param chat_id: int
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError


class Answer(BaseModel, AnswerInterface):
    """Ответ пользователю."""

    chat_id: Optional[int]
    message: str

    async def send(self, chat_id: int = None):
        """Метод для отправки ответа.

        :param chat_id: int
        """
        await get_bot_instance().send_message(chat_id=chat_id or self.chat_id, text=self.message)


class AnswersList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов."""

    def __init__(self, *args: AnswerInterface) -> None:
        super().__init__(args)

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки ответа.

        :param chat_id: int
        """
        for elem in self:
            elem.send(chat_id)
