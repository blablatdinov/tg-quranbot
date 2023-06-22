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
from typing import final

import attrs

from app_types.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.answers.answer import KeyboardInterface
from services.ayats.ayat import Ayat
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard
from services.ayats.enums import AyatCallbackTemplateEnum


@final
@attrs.define
class AyatAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята."""

    _ayat: Ayat
    _favorite_ayats_repo: FavoriteAyatRepositoryInterface
    _neighbor_ayats: NeighborAyatsRepositoryInterface
    _ayat_callback_template: AyatCallbackTemplateEnum

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            NeighborAyatKeyboard(self._neighbor_ayats, self._ayat_callback_template),
            self._favorite_ayats_repo,
        ).generate(update)
