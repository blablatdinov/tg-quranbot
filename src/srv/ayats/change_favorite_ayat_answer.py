# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.fk_async_int import FkAsyncInt
from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerFork,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgChatIdAnswer,
    TgKeyboardEditAnswer,
    TgMessageIdAnswer,
)
from integrations.tg.tg_chat_id import TgChatId
from services.intable_regex import IntableRegex
from services.state_answer import StepAnswer
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.ayat_favorite_status import AyatFavoriteStatus
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.favorite_ayats_after_remove import FavoriteAyatsAfterRemove
from srv.ayats.favorite_neighbor_ayats import FavoriteNeighborAyats
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.pg_neighbor_ayats import PgNeighborAyats
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat
from srv.ayats.text_search_neighbor_ayats import TextSearchNeighborAyats
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
class ChangeFavoriteAyatAnswer(TgAnswer):
    """Ответ на запрос о смене аята в избранном."""

    _pgsql: Database
    _origin: TgAnswer
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        status = AyatFavoriteStatus(str(CallbackQueryData(update)))
        result_ayat = TextLenSafeAyat(
            PgAyat(
                FkAsyncInt(
                    IntableRegex(
                        str(CallbackQueryData(update)),
                    ),
                ),
                self._pgsql,
            ),
        )
        if status.change_to():
            query = '\n'.join([
                'INSERT INTO favorite_ayats',
                '(ayat_id, user_id)',
                'VALUES',
                '(:ayat_id, :user_id)',
            ])
        else:
            query = '\n'.join([
                'DELETE FROM favorite_ayats',
                'WHERE ayat_id = :ayat_id AND user_id = :user_id',
            ])
        await self._pgsql.execute(
            query, {'ayat_id': status.ayat_id(), 'user_id': int(TgChatId(update))},
        )
        chat_id = TgChatId(update)
        return await TgAnswerFork.ctor(
            self._logger,
            StepAnswer(
                UserStep.ayat_favor.value,
                TgChatIdAnswer(
                    TgMessageIdAnswer(
                        TgAnswerMarkup(
                            TgKeyboardEditAnswer(TgAnswerToSender(self._origin)),
                            AyatAnswerKeyboard(
                                result_ayat,
                                FavoriteNeighborAyats(
                                    status.ayat_id(),
                                    FavoriteAyatsAfterRemove(chat_id, status.ayat_id(), self._pgsql),
                                ),
                                AyatCallbackTemplateEnum.get_favorite_ayat,
                                self._pgsql,
                            ),
                        ),
                        TgMessageId(update),
                    ),
                    chat_id,
                ),
                self._redis,
                self._logger,
            ),
            StepAnswer(
                UserStep.ayat_search.value,
                TgChatIdAnswer(
                    TgMessageIdAnswer(
                        TgAnswerMarkup(
                            TgKeyboardEditAnswer(TgAnswerToSender(self._origin)),
                            AyatAnswerKeyboard(
                                result_ayat,
                                TextSearchNeighborAyats.ctor(
                                    self._pgsql,
                                    status.ayat_id(),
                                    AyatTextSearchQuery(self._redis, chat_id, self._logger),
                                ),
                                AyatCallbackTemplateEnum.get_search_ayat,
                                self._pgsql,
                            ),
                        ),
                        TgMessageId(update),
                    ),
                    chat_id,
                ),
                self._redis,
                self._logger,
            ),
            TgChatIdAnswer(
                TgMessageIdAnswer(
                    TgAnswerMarkup(
                        TgKeyboardEditAnswer(TgAnswerToSender(self._origin)),
                        AyatAnswerKeyboard(
                            result_ayat,
                            PgNeighborAyats(
                                self._pgsql, await result_ayat.identifier().ayat_id(),
                            ),
                            AyatCallbackTemplateEnum.get_ayat,
                            self._pgsql,
                        ),
                    ),
                    TgMessageId(update),
                ),
                chat_id,
            ),
        ).build(update)
