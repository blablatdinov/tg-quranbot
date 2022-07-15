from typing import Optional, Union

from aiogram import types
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


def get_default_markup() -> types.ReplyKeyboardMarkup:
    """Получить дефолтную клавиатуру.

    :returns: Keyboard
    """
    return (
        types.ReplyKeyboardMarkup()
        .row(types.KeyboardButton('🎧 Подкасты'))
        .row(types.KeyboardButton('🕋 Время намаза'))
        .row(types.KeyboardButton('🌟 Избранное'), types.KeyboardButton('🔍 Найти аят'))
    )


class Answer(BaseModel, AnswerInterface):
    """Ответ пользователю."""

    chat_id: Optional[int]
    message: Optional[str]
    telegram_file_id: Optional[str]
    link_to_file: Optional[str]
    keyboard: Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup, None]

    class Config:
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

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки ответа.

        :param chat_id: int
        :raises InternalBotError: if not take chat_id
        """
        from exceptions import InternalBotError  # noqa: WPS433

        bot_instance = get_bot_instance()
        markup = self.get_markup()
        chat_id = chat_id or self.chat_id
        if not chat_id:
            raise InternalBotError

        if self.telegram_file_id and not settings.DEBUG:
            await bot_instance.send_audio(chat_id=chat_id, audio=self.telegram_file_id, reply_markup=markup)
        elif self.link_to_file:
            await bot_instance.send_message(chat_id=chat_id, text=self.link_to_file, reply_markup=markup)
        await bot_instance.send_message(chat_id=chat_id, text=self.message, reply_markup=markup)

    def to_list(self) -> list['Answer']:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return [self]


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

    def to_list(self) -> list['Answer']:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return self
