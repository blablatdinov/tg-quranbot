from typing import Optional, Union

from aiogram import types
from pydantic import BaseModel

from services.answer import get_default_markup
from services.answers.interface import AnswerInterface, SingleAnswerInterface
from settings import settings
from utlls import get_bot_instance


class Answer(BaseModel, AnswerInterface, SingleAnswerInterface):
    """Ответ пользователю."""

    chat_id: Optional[int]
    message: Optional[str]
    telegram_file_id: Optional[str]
    link_to_file: Optional[str]
    keyboard: Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup, None]

    class Config(object):
        arbitrary_types_allowed = True

    def get_markup(self) -> Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup]:
        """Получить клавиатуру.

        :returns: Keyboard
        """
        return self.keyboard or get_default_markup()

    async def edit_markup(self, message_id: int, chat_id: int = None) -> None:
        """Редиктировать клавиатуру.

        :param message_id: int
        :param chat_id: int
        """
        chat_id = chat_id or self.chat_id
        bot_instance = get_bot_instance()
        markup = self.get_markup()
        await bot_instance.edit_message_reply_markup(chat_id=chat_id, reply_markup=markup)

    async def send(self, chat_id: int = None) -> list[types.Message]:
        """Метод для отправки ответа.

        :param chat_id: int
        :return: types.Message
        :raises InternalBotError: if not take _chat_id
        """
        from exceptions.base_exception import InternalBotError  # noqa: WPS433

        bot_instance = get_bot_instance()
        markup = self.get_markup()
        chat_id = chat_id or self.chat_id
        if not chat_id:
            raise InternalBotError

        if self.telegram_file_id and not settings.DEBUG:
            message = await bot_instance.send_audio(chat_id=chat_id, audio=self.telegram_file_id, reply_markup=markup)
        elif self.link_to_file:
            message = await bot_instance.send_message(chat_id=chat_id, text=self.link_to_file, reply_markup=markup)
        else:
            message = await bot_instance.send_message(chat_id=chat_id, text=self.message, reply_markup=markup)
        return [message]

    def to_list(self) -> list[SingleAnswerInterface]:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return [self]
