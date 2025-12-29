# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.fk_string import FkString
from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from services.intable_regex import IntableRegex
from srv.ayats.ayat_answer import AyatAnswer
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.ayats_by_text_query import AyatsByTextQuery
from srv.ayats.cached_text_search_query import CachedTextSearchQuery
from srv.ayats.text_search_neighbor_ayats import TextSearchNeighborAyats


@final
@attrs.define(frozen=True)
class SearchAyatByTextCallbackAnswer(TgAnswer):
    """Поиск аята по тексту для обработки нажатия кнопки."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        """
        target_ayat_id = int(IntableRegex(str(CallbackQueryData(update))))
        ayats = await AyatsByTextQuery(
            FkString(
                await AyatTextSearchQuery(
                    self._redis,
                    TgChatId(update),
                    self._logger,
                ).read(),
            ),
            self._pgsql,
        ).to_list()
        for ayat in ayats:
            if await ayat.identifier().ayat_id() == target_ayat_id:
                result_ayat = ayat
                break
        else:
            raise AyatNotFoundError
        return await AyatAnswer(
            self._debug_mode,
            self._empty_answer,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                TextSearchNeighborAyats.ctor(
                    self._pgsql,
                    await result_ayat.identifier().ayat_id(),
                    CachedTextSearchQuery(
                        AyatTextSearchQuery(
                            self._redis,
                            TgChatId(update),
                            self._logger,
                        ),
                    ),
                ),
                AyatCallbackTemplateEnum.get_search_ayat,
                self._pgsql,
            ),
        ).build(update)
