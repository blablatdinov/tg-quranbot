# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.async_supports_str import AsyncSupportsStr
from srv.prayers.prayers_info import PrayersInfo


@final
@attrs.define(frozen=True)
class PrayersText(AsyncSupportsStr):
    """Информация о времени намаза в текстовом виде."""

    _prayer_info: PrayersInfo

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        origin = await self._prayer_info.to_dict()
        template = '\n'.join([
            'Время намаза для г. {city_name} ({date})\n',
            'Иртәнге: {fajr_prayer_time}',
            'Восход: {sunrise_prayer_time}',
            'Өйлә: {dhuhr_prayer_time}',
            'Икенде: {asr_prayer_time}',
            'Ахшам: {magrib_prayer_time}',
            'Ястү: {ishaa_prayer_time}',
        ])
        return template.format(
            city_name=origin['city_name'],
            date=origin['date'],
            fajr_prayer_time=origin['fajr_prayer_time'],
            sunrise_prayer_time=origin['sunrise_prayer_time'],
            dhuhr_prayer_time=origin['dhuhr_prayer_time'],
            asr_prayer_time=origin['asr_prayer_time'],
            magrib_prayer_time=origin['magrib_prayer_time'],
            ishaa_prayer_time=origin['ishaa_prayer_time'],
        )
