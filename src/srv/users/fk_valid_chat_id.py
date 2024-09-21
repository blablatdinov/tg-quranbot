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

from typing import SupportsInt, final, override

import attrs

from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from srv.users.valid_chat_id import ValidChatId


@final
@attrs.define(frozen=True)
class FkValidChatId(ValidChatId):
    """Фейковый объект с валидным идентификатором чата.

    Использовать для случаев создания пользователя если мы уверены в наличии идентификатора в хранилище.
    Например: srv.users.active_users.ActiveUsers
    """

    _origin: AsyncInt

    @classmethod
    def int_ctor(cls, int_value: SupportsInt) -> ValidChatId:
        """Числовой конструктор.

        :param int_value: SupportsInt
        :return: FkValidChatId
        """
        return cls(FkAsyncInt(int_value))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        return await self._origin.to_int()
