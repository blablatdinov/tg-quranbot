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
