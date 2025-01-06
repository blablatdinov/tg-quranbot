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
import httpx

from app_types.listable import AsyncListable


@final
@attrs.define(frozen=True)
class NtCityNames(AsyncListable):
    """Имена городов с сайта https://namaz.today ."""

    _query: str

    @override
    async def to_list(self) -> list[str]:
        """Список строк.

        :returns: list[str]
        """
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get('https://namaz.today/city.php?term={0}'.format(self._query))
            # TODO #1432:30min Обрабатывать не найденные города
            response.raise_for_status()
        # TODO #1432:30min После имплементации #1433 подставлять в city_id реальные значения
        # TODO #1428:30min Определить как у пользователя будет храниться выбранный город
        return [
            city['city']
            for city in response.json()
        ]