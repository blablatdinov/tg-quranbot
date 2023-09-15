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
import datetime
from typing import Sequence, final

import attrs
import httpx
import pytz
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import MessageId
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgKeyboardEditAnswer,
    TgMessageAnswer,
    TgMessageIdAnswer,
    TgTextAnswer,
)
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from services.user_prayer_keyboard import UserPrayersKeyboard
from srv.prayers.invite_set_city_answer import InviteSetCityAnswer, UserWithoutCitySafeAnswer
from srv.prayers.prayers_expired_answer import PrayersExpiredAnswer
from srv.prayers.prayers_text import PrayersText, UserCityId


@final
@attrs.define(frozen=True)
@elegant
class PrayerTimeAnswer(TgAnswer):
    """Ответ с временами намаза.

    _pgsql: Database - соединение с БД postgres
    _origin: TgAnswer - возможно редактирование сообщения при смене статуса или отправка нового сообщения
    _admin_chat_ids: Sequence[int] - список идентификаторов админов
    """

    _pgsql: Database
    _origin: TgAnswer
    _admin_chat_ids: Sequence[int]
    _empty_answer: TgAnswer
    _redis: Redis

    @classmethod
    def new_prayers_ctor(
        cls, pgsql: Database, empty_answer: TgAnswer, admin_chat_ids: Sequence[int], redis: Redis,
    ) -> TgAnswer:
        """Конструктор для генерации времени намаза.

        :param pgsql: Database
        :param empty_answer: TgAnswer
        :param admin_chat_ids: Sequence[int]
        :param redis: Redis
        :return: TgAnswer
        """
        return cls(
            pgsql,
            TgAnswerToSender(TgMessageAnswer(empty_answer)),
            admin_chat_ids,
            empty_answer,
            redis,
        )

    @classmethod
    def edited_markup_ctor(
        cls, pgsql: Database, empty_answer: TgAnswer, admin_chat_ids: Sequence[int], redis: Redis,
    ) -> TgAnswer:
        """Конструктор для времен намаза при смене статуса прочитанности.

        :param pgsql: Database
        :param empty_answer: TgAnswer
        :param admin_chat_ids: Sequence[int]
        :param redis: Redis
        :return: TgAnswer
        """
        return cls(
            pgsql,
            TgAnswerToSender(TgKeyboardEditAnswer(empty_answer)),
            admin_chat_ids,
            empty_answer,
            redis,
        )

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await UserWithoutCitySafeAnswer(
            PrayersExpiredAnswer(
                TgMessageIdAnswer(
                    TgAnswerMarkup(
                        TgTextAnswer(
                            self._origin,
                            PrayersText(
                                self._pgsql,
                                datetime.datetime.now(pytz.timezone('Europe/Moscow')).date(),
                                UserCityId(self._pgsql, TgChatId(update)),
                            ),
                        ),
                        UserPrayersKeyboard(
                            self._pgsql,
                            datetime.datetime.now(pytz.timezone('Europe/Moscow')).date(),
                            TgChatId(update),
                        ),
                    ),
                    int(MessageId(update)),
                ),
                self._empty_answer,
                self._admin_chat_ids,
            ),
            InviteSetCityAnswer(
                TgTextAnswer.str_ctor(
                    TgHtmlMessageAnswerToSender(self._empty_answer),
                    'Отправьте местоположение или воспользуйтесь поиском',
                ),
                self._redis,
            ),
        ).build(update)
