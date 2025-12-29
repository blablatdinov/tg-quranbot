# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
