# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Sequence
from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgHtmlParseAnswer,
    TgKeyboardEditAnswer,
    TgMessageAnswer,
    TgMessageIdAnswer,
    TgTextAnswer,
)
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from integrations.tg.tg_chat_id import TgChatId
from services.user_prayer_keyboard import UserPrayersKeyboard
from settings import Settings
from srv.message_not_found_safe_answer import MessageNotFoundSafeAnswer
from srv.prayers.date_from_user_prayer_id import DateFromUserPrayerId
from srv.prayers.invite_set_city_answer import InviteSetCityAnswer
from srv.prayers.pagination_per_day_date import PaginationPerDayDate
from srv.prayers.pg_prayers_info import PgPrayersInfo
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayers_expired_answer import PrayersExpiredAnswer
from srv.prayers.prayers_mark_as_date import PrayersMarkAsDate
from srv.prayers.prayers_request_date import PrayersRequestDate
from srv.prayers.prayers_text import PrayersText
from srv.prayers.ramadan_prayer_info import RamadanPrayerInfo
from srv.prayers.user_city_id import UserCityId
from srv.prayers.user_without_city_safe_answer import UserWithoutCitySafeAnswer


@final
@attrs.define(frozen=True)
class PgPrayerTimeAnswer(TgAnswer):
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
    _prayers_date: PrayerDate
    _logger: LogSink
    _settings: Settings

    @classmethod
    def new_prayers_ctor(  # noqa: PLR0913
        cls,
        pgsql: Database,
        empty_answer: TgAnswer,
        admin_chat_ids: Sequence[int],
        redis: Redis,
        logger: LogSink,
        settings: Settings,
    ) -> TgAnswer:
        """Конструктор для генерации времени намаза.

        :param pgsql: Database
        :param empty_answer: TgAnswer
        :param admin_chat_ids: Sequence[int]
        :param redis: Redis
        :param logger: LogSink
        :param settings: Settings
        :return: TgAnswer
        """
        return cls(
            pgsql,
            TgAnswerToSender(TgMessageAnswer(empty_answer)),
            admin_chat_ids,
            empty_answer,
            redis,
            PrayersRequestDate(),
            logger,
            settings,
        )

    @classmethod
    def edited_markup_ctor(  # noqa: PLR0913
        cls,
        pgsql: Database,
        empty_answer: TgAnswer,
        admin_chat_ids: Sequence[int],
        redis: Redis,
        logger: LogSink,
        settings: Settings,
    ) -> TgAnswer:
        """Конструктор для времен намаза при смене статуса прочитанности.

        :param pgsql: Database
        :param empty_answer: TgAnswer
        :param admin_chat_ids: Sequence[int]
        :param redis: Redis
        :param logger: LogSink
        :param settings: Settings
        :return: TgAnswer
        """
        return MessageNotFoundSafeAnswer(
            cls(
                pgsql,
                TgAnswerToSender(TgKeyboardEditAnswer(empty_answer)),
                admin_chat_ids,
                empty_answer,
                redis,
                PrayersMarkAsDate(),
                logger,
                settings,
            ),
            cls(
                pgsql,
                TgAnswerToSender(TgMessageAnswer(empty_answer)),
                admin_chat_ids,
                empty_answer,
                redis,
                DateFromUserPrayerId(pgsql),
                logger,
                settings,
            ),
        )

    @classmethod
    def pagination_per_day_ctor(  # noqa: PLR0913
        cls,
        pgsql: Database,
        empty_answer: TgAnswer,
        admin_chat_ids: Sequence[int],
        redis: Redis,
        logger: LogSink,
        settings: Settings,
    ) -> TgAnswer:
        """Конструктор для пагинации по дням.

        :param pgsql: Database
        :param empty_answer: TgAnswer
        :param admin_chat_ids: Sequence[int]
        :param redis: Redis
        :param logger: LogSink
        :param settings: Settings
        :return: TgAnswer
        """
        return cls(
            pgsql,
            TgAnswerToSender(TgMessageAnswer(empty_answer)),
            admin_chat_ids,
            empty_answer,
            redis,
            PaginationPerDayDate(),
            logger,
            settings,
        )

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await UserWithoutCitySafeAnswer(
            PrayersExpiredAnswer(
                TgMessageIdAnswer(
                    TgHtmlParseAnswer(
                        TgAnswerMarkup(
                            TgTextAnswer(
                                self._origin,
                                PrayersText(
                                    RamadanPrayerInfo(
                                        PgPrayersInfo(
                                            self._pgsql,
                                            self._prayers_date,
                                            UserCityId(self._pgsql, TgChatId(update)),
                                            update,
                                        ),
                                        self._settings.RAMADAN_MODE,
                                    ),
                                ),
                            ),
                            UserPrayersKeyboard(
                                self._pgsql,
                                self._prayers_date,
                                TgChatId(update),
                            ),
                        ),
                    ),
                    TgMessageId(update),
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
                self._logger,
            ),
        ).build(update)
