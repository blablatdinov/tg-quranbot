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
from typing import final

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers.interface import TgAnswerInterface


@final
@attrs.define(frozen=True)
@elegant
class ResizedKeyboard(KeyboardInterface):
    """Сжатая в высоту клавиатура."""

    _origin: KeyboardInterface

    async def generate(self, update):
        """Генерация.

        :param update: Update
        :return: str
        """
        origin_keyboard = await self._origin.generate(update)
        keyboard_as_dict = json.loads(origin_keyboard)
        keyboard_as_dict['resize_keyboard'] = True
        return json.dumps(keyboard_as_dict)


@final
@elegant
class DefaultKeyboard(KeyboardInterface):
    """Класс клавиатуры по умолчанию."""

    async def generate(self, update: Update):
        """Генерация.

        :param update: Update
        :return: str
        """
        return '{"keyboard":[["🎧 Подкасты"],["🕋 Время намаза","🏘️ Поменять город"],["🌟 Избранное","🔍 Найти аят"]]}'


@final
@attrs.define(frozen=True)
@elegant
class FileAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    _debug_mode: bool
    _telegram_file_id_answer: TgAnswerInterface
    _file_link_answer: TgAnswerInterface

    async def build(self, update) -> list[httpx.Request]:
        """Отправка.

        :param update: Update
        :return: list[httpx.Request]
        """
        if self._debug_mode:
            return await self._file_link_answer.build(update)
        return await self._telegram_file_id_answer.build(update)


@final
@attrs.define(frozen=True)
@elegant
class TelegramFileIdAnswer(TgAnswerInterface):
    """Класс ответа с файлом."""

    _origin: TgAnswerInterface
    _telegram_file_id: str | None

    async def build(self, update: Update) -> list[httpx.Request]:
        """Отправка.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.copy_add_param('audio', self._telegram_file_id))
            for request in await self._origin.build(update)
        ]
