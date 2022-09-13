from typing import Optional, Union

import httpx
from aiogram import types

from integrations.tg.tg_answers.interface import TgAnswerInterface


class KeyboardInterface(object):
    """Интерфейс клавиатуры."""

    async def generate(self) -> Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup]:
        """Генерация.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class DefaultKeyboard(KeyboardInterface):
    """Класс клавиатуры по умолчанию."""

    async def generate(self):
        """Генерация.

        :return: types.ReplyKeyboardMarkup
        """
        return (
            types.ReplyKeyboardMarkup(resize_keyboard=True)
            .row(types.KeyboardButton('🎧 Подкасты'))
            .row(types.KeyboardButton('🕋 Время намаза'))
            .row(types.KeyboardButton('🌟 Избранное'), types.KeyboardButton('🔍 Найти аят'))
        )


class FileAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    def __init__(self, debug_mode: bool, telegram_file_id_answer: TgAnswerInterface, file_link_answer: TgAnswerInterface):
        self._debug_mode = debug_mode
        self._telegram_file_id_answer = telegram_file_id_answer
        self._file_link_answer = file_link_answer

    async def build(self, update) -> list[httpx.Request]:
        """Отправка.

        :return: list[httpx.Request]
        """
        if self._debug_mode:
            return await self._file_link_answer.build(update)

        return await self._telegram_file_id_answer.build(update)


class TelegramFileIdAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    def __init__(self, answer: TgAnswerInterface, telegram_file_id: Optional[str]):
        self._origin = answer
        self._telegram_file_id = telegram_file_id

    async def build(self, update) -> list[httpx.Request]:
        """Отправка.

        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.copy_add_param('audio_id', self._telegram_file_id))
            for request in await self._origin.build(update)
        ]
