import asyncio
from typing import Optional, Union

from aiogram import types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, UserDeactivated
from pydantic import BaseModel

from repository.users.users import UsersRepositoryInterface
from settings import settings
from utlls import get_bot_instance


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


class SpamAnswerList(list, AnswerInterface):  # noqa: WPS600
    """Список ответов для рассылки.

    Отправляет сообщения пачками
    """

    _users_repository: UsersRepositoryInterface
    _unsubscriber_user_chat_ids: list[int] = []

    def __init__(self, users_repository: UsersRepositoryInterface, *args: AnswerInterface) -> None:
        self._users_repository = users_repository
        super().__init__(args)

    async def send(self, chat_id: int = None) -> None:
        """Метод для отправки ответа.

        :param chat_id: int
        """
        self._validate()
        for index in range(0, len(self), 100):
            tasks = []
            for answer in self[index:index + 100]:
                tasks.append(self._send_one_answer(answer))

            await asyncio.gather(*tasks)

        if self._unsubscriber_user_chat_ids:
            await self._users_repository.update_status(self._unsubscriber_user_chat_ids, to=False)

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        for elem in self:
            await elem.edit_markup(chat_id)

    def to_list(self) -> list['Answer']:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return self

    async def _send_one_answer(self, answer: Answer):
        try:
            await answer.send()
        except (ChatNotFound, BotBlocked, UserDeactivated):
            # answer.chat_id is not None already checked in self._validate method
            self._unsubscriber_user_chat_ids.append(answer.chat_id)  # type: ignore

    def _validate(self) -> None:
        # cycle import protect
        from exceptions import InternalBotError  # noqa: WPS433
        answers_chat_ids = {answer.chat_id for answer in self}
        if None in answers_chat_ids:
            raise InternalBotError


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

    async def edit_markup(self, message_id: int, chat_id: int = None):
        """Метод для редактирования сообщения.

        :param chat_id: int
        :param message_id: int
        """
        for elem in self:
            await elem.edit_markup(chat_id)

    def to_list(self) -> list['Answer']:
        """Форматировать в строку из элементов.

        :returns: list[Answer]
        """
        return self
