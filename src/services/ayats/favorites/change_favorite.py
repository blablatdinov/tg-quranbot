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
from databases import Database

from app_types.intable import SyncToAsyncIntable
from app_types.update import Update
from db.connection import database
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import MessageId
from integrations.tg.tg_answers import (
    TgAnswerInterface,
    TgAnswerMarkup,
    TgChatIdAnswer,
    TgKeyboardEditAnswer,
    TgMessageIdAnswer,
)
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.ayats.ayat import QAyat
from services.ayats.enums import AyatCallbackTemplateEnum
from services.ayats.favorite_ayats import FavoriteAyatStatus
from services.ayats.keyboards import AyatAnswerKeyboard
from services.regular_expression import IntableRegularExpression


@final
class ChangeFavoriteAyatAnswer(TgAnswerInterface):
    """Ответ на запрос о смене аята в избранном."""

    def __init__(
        self,
        connection: Database,
        answer: TgAnswerInterface,
    ):
        """Конструктор класса.

        :param connection: Database
        :param answer: TgAnswerInterface
        """
        self._origin = answer
        self._connection = connection

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        status = FavoriteAyatStatus(str(CallbackQueryData(update)))
        result_ayat = QAyat(
            SyncToAsyncIntable(
                IntableRegularExpression(
                    str(CallbackQueryData(update)),
                ),
            ),
            database,
        )
        if status.change_to():
            query = """
                INSERT INTO favorite_ayats
                (ayat_id, user_id)
                VALUES
                (:ayat_id, :user_id)
            """
        else:
            query = """
                DELETE FROM favorite_ayats
                WHERE ayat_id = :ayat_id AND user_id = :user_id
            """
        await self._connection.execute(
            query, {'ayat_id': status.ayat_id(), 'user_id': int(TgChatId(update))},
        )
        return await TgChatIdAnswer(
            TgMessageIdAnswer(
                TgAnswerMarkup(
                    TgKeyboardEditAnswer(self._origin),
                    AyatAnswerKeyboard(
                        result_ayat,
                        FavoriteAyatsRepository(database),
                        NeighborAyats(
                            database, await result_ayat.id(),
                        ),
                        AyatCallbackTemplateEnum.get_favorite_ayat,
                    ),
                ),
                int(MessageId(update)),
            ),
            int(TgChatId(update)),
        ).build(update)
