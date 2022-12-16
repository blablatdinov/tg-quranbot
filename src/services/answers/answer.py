import json
from typing import Optional

import httpx

from app_types.stringable import Stringable
from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers.interface import TgAnswerInterface


class ResizedKeyboard(KeyboardInterface):
    """Сжатая в высоту клавиатура."""

    def __init__(self, keyboard: KeyboardInterface):
        self._origin = keyboard

    async def generate(self, update):
        """Генерация.

        :param update: Stringable
        :return: str
        """
        origin_keyboard = await self._origin.generate(update)
        keyboard_as_dict = json.loads(origin_keyboard)
        keyboard_as_dict['resize_keyboard'] = True
        return json.dumps(keyboard_as_dict)


class DefaultKeyboard(KeyboardInterface):
    """Класс клавиатуры по умолчанию."""

    async def generate(self, update: Stringable):
        """Генерация.

        :param update: Stringable
        :return: str
        """
        return '{"keyboard":[["🎧 Подкасты"],["🕋 Время намаза"],["🌟 Избранное","🔍 Найти аят"]]}'


class FileAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    def __init__(
        self,
        debug_mode: bool,
        telegram_file_id_answer: TgAnswerInterface,
        file_link_answer: TgAnswerInterface,
    ):
        self._debug_mode = debug_mode
        self._telegram_file_id_answer = telegram_file_id_answer
        self._file_link_answer = file_link_answer

    async def build(self, update) -> list[httpx.Request]:
        """Отправка.

        :param update: Stringable
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

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Отправка.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.copy_add_param('audio', self._telegram_file_id))
            for request in await self._origin.build(update)
        ]
