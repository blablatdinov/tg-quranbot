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
from contextlib import suppress
from typing import final

from app_types.update import Update
from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.answers.answer import KeyboardInterface
from services.ayats.enums import AyatCallbackTemplateEnum


@final
class NeighborAyatKeyboard(KeyboardInterface):
    """Клавиатура с соседними аятами."""

    def __init__(self, ayats_neighbors: NeighborAyatsRepositoryInterface, callback_template: AyatCallbackTemplateEnum):
        """Конструктор класса.

        :param ayats_neighbors: NeighborAyatsRepositoryInterface
        :param callback_template: AyatCallbackTemplateEnum
        """
        self._ayats_neighbors = ayats_neighbors
        self._callback_template = callback_template

    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        buttons = []
        with suppress(AyatNotFoundError):
            left = await self._ayats_neighbors.left_neighbor()
            buttons.append({
                'text': '<- {0}:{1}'.format(left.sura_num, left.ayat_num),
                'callback_data': self._callback_template.format(left.id),
            })
        buttons.append({
            'text': await self._ayats_neighbors.page(),
            'callback_data': 'fake',
        })
        with suppress(AyatNotFoundError):
            right = await self._ayats_neighbors.right_neighbor()
            buttons.append({
                'text': '{0}:{1} ->'.format(right.sura_num, right.ayat_num),
                'callback_data': self._callback_template.format(right.id),
            })
        return json.dumps({
            'inline_keyboard': [buttons],
        })
