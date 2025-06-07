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
from databases import Database
from furl import furl

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.internal_exceptions import CityNotFoundError
from srv.prayers.city import City


@final
@attrs.define(frozen=True)
class HgPrayersUrl(AsyncSupportsStr):
    """Url, по которому можно посмотреть время намаза для города на сайте https://halalguide.me .

    Пример: https://halalguide.me/kazan/namaz-time/june-2025
    """

    _city: City
    _pgsql: Database
    _date: datetime.date

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        link = await self._pgsql.fetch_val(
            'SELECT link FROM halal_guide_cities WHERE city_id = :city_id',
            {'city_id': str(await self._city.city_id())},
        )
        if not link:
            raise CityNotFoundError
        return str(
            furl(link) / '{0}-{1}'.format(
                self._date.strftime('%B').lower(),
                self._date.year,
            ),
        )
