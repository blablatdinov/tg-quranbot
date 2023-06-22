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

from app_types.update import Update
from db.connection import database
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from services.ayats.ayat_answer import AyatAnswer
from services.ayats.enums import AyatCallbackTemplateEnum
from services.ayats.favorites.favorite_ayats import FavoriteAyats
from services.ayats.keyboards import AyatAnswerKeyboard
from services.regular_expression import IntableRegularExpression


@final
@attrs.define
class FavoriteAyatStatus(object):
    """Пользовательский ввод статуса аята в избранном."""

    _source: str

    def ayat_id(self) -> int:
        """Идентификатор аята.

        :return: int
        """
        return int(IntableRegularExpression(self._source))

    def change_to(self) -> bool:
        """Целевое значение.

        :return: bool
        """
        return 'addToFavor' in self._source


@final
@attrs.define
class FavoriteAyatAnswer(TgAnswerInterface):
    """Ответ с избранными аятами."""

    _debug_mode: bool
    _message_answer: TgAnswerInterface
    _file_answer: TgAnswerInterface
    _favorite_ayats_repo: FavoriteAyatRepositoryInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = (
            await FavoriteAyats(
                TgChatId(update),
                database,
            ).to_list()
        )[0]
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                self._favorite_ayats_repo,
                FavoriteNeighborAyats(
                    await result_ayat.id(), int(TgChatId(update)), self._favorite_ayats_repo,
                ),
                AyatCallbackTemplateEnum.get_favorite_ayat,
            ),
        ).build(update)


@final
@attrs.define
class FavoriteAyatEmptySafeAnswer(TgAnswerInterface):
    """Обработка ошибок с пустыми избранными."""

    _origin: TgAnswerInterface
    _error_answer: TgAnswerInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except IndexError:
            return await self._error_answer.build(update)


@final
@attrs.define
class FavoriteAyatPage(TgAnswerInterface):
    """Страница с избранным аятом."""

    _debug_mode: bool
    _message_answer: TgAnswerInterface
    _file_answer: TgAnswerInterface
    _favorite_ayats_repo: FavoriteAyatRepositoryInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = (
            await FavoriteAyats(
                TgChatId(update),
                database,
            ).to_list()
        )[0]
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                self._favorite_ayats_repo,
                FavoriteNeighborAyats(
                    await result_ayat.id(),
                    int(TgChatId(update)),
                    self._favorite_ayats_repo,
                ),
                AyatCallbackTemplateEnum.get_favorite_ayat,
            ),
        ).build(update)
