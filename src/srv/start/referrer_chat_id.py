# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from pyeo import elegant

from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from exceptions.base_exception import BaseAppError
from exceptions.user import StartMessageNotContainReferrerError
from services.instable_regex import IntableRegex
from srv.users.pg_user import PgUser
from srv.users.pg_valid_chat_id import PgValidChatId


@final
@attrs.define(frozen=True)
@elegant
class ReferrerChatId(AsyncInt):
    """Идентификатор чата пригласившего."""

    _message: str
    _pgsql: Database

    @override
    async def to_int(self) -> int:
        """Получить идентификатор пригласившего.

        :return: int
        :raises StartMessageNotContainReferrerError: if message not contain referrer id
        """
        try:
            message_meta = int(IntableRegex(self._message))
        except BaseAppError as err:
            raise StartMessageNotContainReferrerError from err
        max_legacy_id = 3000
        if message_meta < max_legacy_id:
            return await PgUser.legacy_id_ctor(
                FkAsyncInt(
                    IntableRegex(self._message),
                ),
                self._pgsql,
            ).chat_id()
        return await PgUser(
            PgValidChatId.int_ctor(
                self._pgsql,
                IntableRegex(self._message),
            ),
            self._pgsql,
        ).chat_id()
