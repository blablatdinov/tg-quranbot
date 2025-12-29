# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
