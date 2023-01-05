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

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import Ayat
from services.answers.answer import KeyboardInterface


class AyatFavoriteKeyboardButton(KeyboardInterface):
    """Кнопка с добавлением аята в избранные."""

    def __init__(self, ayat: Ayat, keyboard: KeyboardInterface, favorite_ayat_repo: FavoriteAyatRepositoryInterface):
        """Конструктор класса.

        :param ayat: Ayat
        :param keyboard: KeyboardInterface
        :param favorite_ayat_repo: FavoriteAyatRepositoryInterface
        """
        self._ayat = ayat
        self._origin = keyboard
        self._favorite_ayat_repo = favorite_ayat_repo

    async def generate(self, update: Stringable) -> str:
        """Генерация клавиатуры.

        :param update: Stringable
        :return: str
        """
        keyboard = json.loads(await self._origin.generate(update))
        is_favor = await self._favorite_ayat_repo.check_ayat_is_favorite_for_user(
            self._ayat.id,
            int(TgChatId(update)),
        )
        keyboard['inline_keyboard'].append([{
            'text': 'Удалить из избранного' if is_favor else 'Добавить в избранное',
            'callback_data': ('removeFromFavor({0})' if is_favor else 'addToFavor({0})').format(self._ayat.id),
        }])
        return json.dumps(keyboard)
