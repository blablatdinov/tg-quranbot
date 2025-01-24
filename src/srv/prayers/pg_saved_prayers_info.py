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
from typing import final, override

import attrs
import httpx
import pytz
from databases import Database
from lxml import etree

from app_types.fk_update import FkUpdate
from exceptions.prayer_exceptions import PrayersNotFoundError
from srv.prayers.city import City
from srv.prayers.nt_prayers_url import NtPrayersUrl
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo
from exceptions.internal_exceptions import CityNotFoundError, PrayerAtUserAlreadyExistsError, PrayerNotCreatedError, PrayerAlreadyExistsError
from asyncpg.exceptions import UniqueViolationError
from srv.prayers.pg_new_prayers import PgNewPrayers

@final
@attrs.define(frozen=True)
class PgSavedPrayersInfo(PrayersInfo):
    """Информация о времени намаза, сохраненная в postgres."""

    _origin: PrayersInfo
    _pgsql: Database

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        origin = await self._origin.to_dict()
        assert False
        await PgNewPrayers(
            origin,
            self._pgsql,
        ).create()
        return origin
