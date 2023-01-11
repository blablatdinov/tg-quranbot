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

from app_types.stringable import Stringable
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.answers.answer import KeyboardInterface
from services.ayats.ayat import Ayat
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard


@final
class AyatAnswerKeyboard(KeyboardInterface):
    """Клавиатура аята."""

    def __init__(
        self,
        ayat: Ayat,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
        neighbor_ayats: NeighborAyatsRepositoryInterface,
        ayat_callback_template: AyatCallbackTemplate,
    ):
        """Конструктор класса.

        :param ayat: Ayat
        :param favorite_ayats_repo: FavoriteAyatRepositoryInterface
        :param neighbor_ayats: NeighborAyatsRepositoryInterface
        :param ayat_callback_template: AyatCallbackTemplate
        """
        self._ayat = ayat
        self._favorite_ayats_repo = favorite_ayats_repo
        self._neighbor_ayats = neighbor_ayats
        self._ayat_callback_template = ayat_callback_template

    async def generate(self, update: Stringable) -> str:
        """Генерация.

        :param update: Stringable
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            self._ayat,
            NeighborAyatKeyboard(self._neighbor_ayats, self._ayat_callback_template),
            self._favorite_ayats_repo,
        ).generate(update)
