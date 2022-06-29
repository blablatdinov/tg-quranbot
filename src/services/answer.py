from typing import Optional

from pydantic import BaseModel

from settings import settings
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
    message: Optional[str]
    telegram_file_id: Optional[str]
    link_to_file: Optional[str]

    async def send(self, chat_id: int = None):
        """Метод для отправки ответа.

        :param chat_id: int
        :raises InternalBotError: if not take chat_id
        """
        from exceptions import InternalBotError  # noqa: WPS433

        bot_instance = get_bot_instance()
        chat_id = chat_id or self.chat_id
        if not chat_id:
            raise InternalBotError

        if self.telegram_file_id and not settings.DEBUG:
            await bot_instance.send_audio(chat_id=chat_id, audio=self.telegram_file_id)
        elif self.link_to_file:
            await bot_instance.send_message(chat_id=chat_id, text=self.link_to_file)
        await bot_instance.send_message(chat_id=chat_id, text=self.message)


class AnswersList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов."""

    def __init__(self, *args: AnswerInterface) -> None:
        super().__init__(args)

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки ответа.

        :param chat_id: int
        """
        for elem in self:
            await elem.send(chat_id)
