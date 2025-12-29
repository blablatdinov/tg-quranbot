# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Sequence
from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.prayer_exceptions import PrayersNotFoundError
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerList,
    TgAnswerToSender,
    TgChatIdAnswer,
    TgMessageAnswer,
    TgTextAnswer,
)


@final
@attrs.define(frozen=True)
class PrayersExpiredAnswer(TgAnswer):
    """Декоратор для обработки случаев с отсутствием времени намаза на эту дату."""

    _origin: TgAnswer
    _empty_answer: TgAnswer
    _admin_chat_ids: Sequence[int]

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except PrayersNotFoundError as err:
            return await TgAnswerList.ctor(
                TgTextAnswer.str_ctor(
                    TgAnswerToSender(TgMessageAnswer(self._empty_answer)),
                    'Время намаза на {0} для города {1} не найдено'.format(
                        err.date.strftime('%d.%m.%Y'), err.city_name or '',
                    ),
                ),
                TgTextAnswer.str_ctor(
                    TgChatIdAnswer(
                        TgMessageAnswer(self._empty_answer),
                        self._admin_chat_ids[0],
                    ),
                    'Время намаза на {0} для города {1} не найдено'.format(
                        err.date.strftime('%d.%m.%Y'), err.city_name or '',
                    ),
                ),
            ).build(update)
