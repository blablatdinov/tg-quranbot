# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from contextlib import suppress
from typing import final, override

import attrs
import pytz
from databases import Database

from exceptions.internal_exceptions import PrayerAtUserAlreadyExistsError
from integrations.tg.fk_chat_id import ChatId
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class NtUserPrayersInfo(PrayersInfo):
    """Декоратор для создания записи о времени намаза в таблице prayers_at_user."""

    _origin: PrayersInfo
    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        origin = await self._origin.to_dict()
        day = (
            datetime.datetime
            .strptime(origin['date'], '%d.%m.%Y')
            .replace(tzinfo=pytz.timezone('Europe/Moscow'))
            .date()
        )
        with suppress(PrayerAtUserAlreadyExistsError):
            await PgNewPrayersAtUser(int(self._chat_id), self._pgsql).create(day)
        return origin
