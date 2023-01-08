"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json
from typing import Optional, final

import httpx

from app_types.stringable import Stringable
from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers.interface import TgAnswerInterface


@final
class ResizedKeyboard(KeyboardInterface):
    """Сжатая в высоту клавиатура."""

    def __init__(self, keyboard: KeyboardInterface):
        """Конструктор класса.

        :param keyboard: KeyboardInterface
        """
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


@final
class DefaultKeyboard(KeyboardInterface):
    """Класс клавиатуры по умолчанию."""

    async def generate(self, update: Stringable):
        """Генерация.

        :param update: Stringable
        :return: str
        """
        return '{"keyboard":[["🎧 Подкасты"],["🕋 Время намаза"],["🌟 Избранное","🔍 Найти аят"]]}'


@final
class FileAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    def __init__(
        self,
        debug_mode: bool,
        telegram_file_id_answer: TgAnswerInterface,
        file_link_answer: TgAnswerInterface,
    ):
        """Конструктор класса.

        :param debug_mode: bool
        :param telegram_file_id_answer: TgAnswerInterface
        :param file_link_answer: TgAnswerInterface
        """
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


@final
class TelegramFileIdAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    def __init__(self, answer: TgAnswerInterface, telegram_file_id: Optional[str]):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param telegram_file_id: Optional[str]
        """
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
