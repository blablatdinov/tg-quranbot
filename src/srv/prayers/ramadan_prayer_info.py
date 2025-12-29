# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from copy import deepcopy
from typing import final, override

import attrs

from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class RamadanPrayerInfo(PrayersInfo):
    """Изменяющий декоратор для обозначения времени сухура и ифтара."""

    _origin: PrayersInfo
    _ramadan_mode: bool

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с преобразованным временем сухура и ифтара.

        :return: str
        """
        if not self._ramadan_mode:
            return await self._origin.to_dict()
        source_dict = deepcopy(await self._origin.to_dict())
        source_dict['fajr_prayer_time'] = '{0} <i>- Конец сухура</i>'.format(source_dict['fajr_prayer_time'])
        source_dict['magrib_prayer_time'] = '{0} <i>- Ифтар</i>'.format(source_dict['magrib_prayer_time'])
        return source_dict
