# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson
from redis.asyncio import Redis

from app_types.fk_update import FkUpdate
from app_types.logger import LogSink
from srv.prayers.city import City
from srv.prayers.prayer_date import PrayerDate
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class CdPrayersInfo(PrayersInfo):
    """Кэширующий декоратор."""

    _origin: PrayersInfo
    _rds: Redis
    _city: City
    _date: PrayerDate
    _logger: LogSink

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        key = 'prayers:{0}:{1}'.format(
            await self._city.name(),
            (await self._date.parse(FkUpdate.empty_ctor())).strftime('%Y-%m-%d'),
        )
        cached = await self._rds.get(key)
        if cached:
            self._logger.debug('Cache by key {} found, value: {}', key, cached)
            return ujson.loads(cached)
        origin = await self._origin.to_dict()
        await self._rds.set(key, ujson.dumps(origin))
        self._logger.debug('Cache by key {} written, value: {}', key, origin)
        return origin
