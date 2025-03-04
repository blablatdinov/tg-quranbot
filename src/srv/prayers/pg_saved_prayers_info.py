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

from typing import final, override

import attrs
from databases import Database

from app_types.logger import LogSink
from exceptions.internal_exceptions import PrayerAlreadyExistsError
from srv.prayers.pg_new_prayers import PgNewPrayers
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class PgSavedPrayersInfo(PrayersInfo):
    """Информация о времени намаза, сохраненная в postgres."""

    _origin: PrayersInfo
    _pgsql: Database
    _logger: LogSink

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        origin = await self._origin.to_dict()
        try:
            await PgNewPrayers(
                origin,
                self._pgsql,
            ).create()
        except PrayerAlreadyExistsError:
            self._logger.info('Prayer info "{0}" already exists'.format(origin))
        return origin
