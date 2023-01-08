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

import httpx

from app_types.stringable import Stringable
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from services.ayats.ayat_answer import AyatAnswer
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.keyboards import AyatAnswerKeyboard
from services.regular_expression import IntableRegularExpression


@final
class FavoriteAyatStatus(object):
    """Пользовательский ввод статуса аята в избранном."""

    def __init__(self, source: str):
        """Конструктор класса.

        :param source: str
        """
        self._source = source

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
class FavoriteAyatAnswer(TgAnswerInterface):
    """Ответ с избранными аятами."""

    def __init__(
        self,
        debug: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ):
        """Конструктор класса.

        :param debug: bool
        :param message_answer: TgAnswerInterface
        :param file_answer: TgAnswerInterface
        :param favorite_ayats_repo: FavoriteAyatRepositoryInterface
        """
        self._debug_mode = debug
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._favorite_ayats_repo = favorite_ayats_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = (await self._favorite_ayats_repo.get_favorites(int(TgChatId(update))))[0]
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                self._favorite_ayats_repo,
                FavoriteNeighborAyats(
                    result_ayat.id, int(TgChatId(update)), self._favorite_ayats_repo,
                ),
                AyatCallbackTemplate.get_favorite_ayat,
            ),
        ).build(update)


@final
class FavoriteAyatEmptySafeAnswer(TgAnswerInterface):
    """Обработка ошибок с пустыми избранными."""

    def __init__(self, sender_answer: TgAnswerInterface, error_answer: TgAnswerInterface):
        """Конструктор класса.

        :param sender_answer: TgAnswerInterface
        :param error_answer: TgAnswerInterface
        """
        self._origin = sender_answer
        self._error_answer = error_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except IndexError:
            return await self._error_answer.build(update)


@final
class FavoriteAyatPage(TgAnswerInterface):
    """Страница с избранным аятом."""

    def __init__(
        self,
        debug: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ):
        """Конструктор класса.

        :param debug: bool
        :param message_answer: TgAnswerInterface
        :param file_answer: TgAnswerInterface
        :param favorite_ayats_repo: FavoriteAyatRepositoryInterface
        """
        self._debug_mode = debug
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._favorite_ayats_repo = favorite_ayats_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = await self._favorite_ayats_repo.get_favorite(
            int(IntableRegularExpression(str(CallbackQueryData(update)))),
        )
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                self._favorite_ayats_repo,
                FavoriteNeighborAyats(result_ayat.id, int(TgChatId(update)), self._favorite_ayats_repo),
                AyatCallbackTemplate.get_favorite_ayat,
            ),
        ).build(update)
