# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import datetime
import uuid
from operator import add
from typing import Final, final, override

import attrs
import pytz
import ujson
from databases import Database
from eljson.json import Json
from redis.asyncio import Redis

from app_types.fk_async_listable import FkAsyncListable
from app_types.fk_update import FkUpdate
from app_types.logger import LogSink
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerMarkup,
    TgChatIdAnswer,
    TgHtmlParseAnswer,
    TgMessageAnswer,
    TgTextAnswer,
)
from integrations.tg.tg_chat_id import TgChatId
from services.logged_answer import LoggedAnswer
from services.user_prayer_keyboard import UserPrayersKeyboard
from settings import Settings
from srv.events.recieved_event import ReceivedEvent
from srv.events.sink import Sink
from srv.prayers.fk_prayer_date import FkPrayerDate
from srv.prayers.pg_prayers_text import PgPrayersText
from srv.prayers.ramadan_prayer_text import RamadanPrayerText
from srv.prayers.user_city_id import UserCityId
from srv.users.fk_user import FkUser
from srv.users.pg_updated_users_status import PgUpdatedUsersStatus
from srv.users.updated_users_status_event import UpdatedUsersStatusEvent
from srv.users.user import User

CHAT_ID: Final = 'chat_id'


@final
@attrs.define(frozen=True)
class PrayersMailingPublishedEvent(ReceivedEvent):
    """Обработка события о рассылке времени намаза на следующий день."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _settings: Settings
    _events_sink: Sink
    _log_sink: LogSink
    _redis: Redis

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработка события.

        :param json_doc: Json
        """
        active_users = await self._pgsql.fetch_all('\n'.join([
            'SELECT u.chat_id',
            'FROM users AS u',
            "WHERE u.is_active = 't' {0}".format(
                'AND u.chat_id IN ({0})'.format(
                    ','.join([str(chat_id) for chat_id in self._settings.ADMIN_CHAT_IDS]),
                )
                if self._settings.DAILY_PRAYERS == 'off' else '',
            ),
            'ORDER BY u.chat_id',
        ]))
        unsubscribed_users: list[User] = []
        date = FkPrayerDate(
            add(
                datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')),
                datetime.timedelta(days=1),
            ).date(),
        )
        for active_user in active_users:
            await self._iteration(
                TgHtmlParseAnswer(
                    TgAnswerMarkup(
                        TgChatIdAnswer(
                            TgTextAnswer(
                                TgMessageAnswer(self._empty_answer),
                                RamadanPrayerText(
                                    PgPrayersText(
                                        self._pgsql,
                                        date,
                                        UserCityId(self._pgsql, active_user[CHAT_ID]),
                                        FkUpdate.empty_ctor(),
                                    ),
                                    self._settings.RAMADAN_MODE,
                                ),
                            ),
                            active_user[CHAT_ID],
                        ),
                        UserPrayersKeyboard(
                            self._pgsql,
                            date,
                            TgChatId(FkUpdate(ujson.dumps({'chat': {'id': active_user[CHAT_ID]}}))),
                        ),
                    ),
                ),
                active_user[CHAT_ID],
                unsubscribed_users,
            )
        await UpdatedUsersStatusEvent(
            PgUpdatedUsersStatus(self._pgsql, FkAsyncListable(unsubscribed_users)),
            FkAsyncListable(unsubscribed_users),
            self._events_sink,
        ).update(to=False)

    async def _iteration(  # noqa: NPM100. Fix it
        self,
        answer: TgAnswer,
        chat_id: int,
        unsubscribed_users: list[User],
    ) -> None:
        try:
            await LoggedAnswer(
                SendableAnswer(
                    answer,
                    self._log_sink,
                ),
                self._events_sink,
                uuid.uuid4(),
            ).send(FkUpdate.empty_ctor())
        except TelegramIntegrationsError as err:
            error_messages = [
                'chat not found',
                'bot was blocked by the user',
                'user is deactivated',
            ]
            for error_message in error_messages:
                if error_message in str(err):
                    unsubscribed_users.append(FkUser(chat_id, 0, is_active=False))  # noqa: PERF401
