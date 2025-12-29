# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from contextlib import suppress
from typing import final, override

import attrs
import ujson
from databases import Database

from app_types.update import Update
from exceptions.internal_exceptions import PrayerAtUserAlreadyExistsError
from integrations.tg.fk_chat_id import ChatId
from services.answers.resized_keyboard import Keyboard
from srv.prayers.pg_city_change_safe_user_prayers import PgCityChangeSafeUserPrayers
from srv.prayers.pg_exist_user_prayers import PgExistUserPrayers
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
class UserPrayersKeyboard(Keyboard):
    """Клавиатура времен намаза."""

    _pgsql: Database
    _date: PrayerDate
    _chat_id: ChatId

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        parsed_date = await self._date.parse(update)
        with suppress(PrayerAtUserAlreadyExistsError):
            await PgCityChangeSafeUserPrayers(
                PgNewPrayersAtUser(
                    self._chat_id,
                    self._pgsql,
                ),
                PgExistUserPrayers(
                    self._pgsql,
                    self._chat_id,
                    parsed_date,
                ),
            ).create(parsed_date)
        prayers = await PgExistUserPrayers(
            self._pgsql,
            self._chat_id,
            parsed_date,
        ).fetch()
        readed_buttons_line = [
            {
                'text': '✅' if user_prayer['is_read'] else '❌',
                'callback_data': (
                    'mark_not_readed({0})' if user_prayer['is_read'] else 'mark_readed({0})'
                ).format(
                    user_prayer['prayer_at_user_id'],
                ),
            }
            for user_prayer in prayers
        ]
        return ujson.dumps({
            'inline_keyboard': [
                readed_buttons_line,
                [
                    {
                        'text': '<- {0}'.format((parsed_date - datetime.timedelta(days=1)).strftime('%d.%m')),
                        'callback_data': 'pagPrDay({0})'.format(
                            (parsed_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                        ),
                    },
                    {
                        'text': '{0} ->'.format((parsed_date + datetime.timedelta(days=1)).strftime('%d.%m')),
                        'callback_data': 'pagPrDay({0})'.format(
                            (parsed_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                        ),
                    },
                ],
            ],
        })
