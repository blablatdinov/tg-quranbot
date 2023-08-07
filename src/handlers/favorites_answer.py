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
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from services.ayats.favorite_ayats import FavoriteAyatEmptySafeAnswer, FavoriteAyatAnswer


@final
@attrs.define(frozen=True)
@elegant
class FavoriteAyatsAnswer(TgAnswerInterface):
    """Ответ с временами намаза."""

    _database: Database
    _redis: Redis
    _answer_to_sender: TgAnswerInterface
    _html_sender: TgAnswerInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await FavoriteAyatEmptySafeAnswer(
            FavoriteAyatAnswer(
                self._debug,
                self._html_to_sender,
                self._audio_to_sender,
                FavoriteAyatsRepository(self._database),
            ),
            TgTextAnswer(
                self._answer_to_sender,
                'Вы еще не добавляли аятов в избранное',
            ),
        ).build(update)
