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

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.fk_chat_id import ChatId


@final
@attrs.define(frozen=True)
class UserCityId(AsyncSupportsStr):
    """Идентификатор города."""

    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        :raises UserHasNotCityIdError: user has not set city
        """
        query = '\n'.join([
            'SELECT c.city_id',
            'FROM cities AS c',
            'INNER JOIN users AS u ON u.city_id = c.city_id',
            'WHERE u.chat_id = :chat_id',
        ])
        city_name = await self._pgsql.fetch_val(query, {'chat_id': int(self._chat_id)})
        if not city_name:
            raise UserHasNotCityIdError
        return city_name
