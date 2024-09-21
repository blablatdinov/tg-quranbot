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

from contextlib import suppress
from typing import final, override

import attrs

from app_types.async_int_or_none import AsyncIntOrNone
from app_types.intable import AsyncInt
from exceptions.internal_exceptions import UserNotFoundError
from exceptions.user import StartMessageNotContainReferrerError


@final
@attrs.define(frozen=True)
class ReferrerIdOrNone(AsyncIntOrNone):
    """Идентификатор чата пригласившего."""

    _origin: AsyncInt

    @override
    async def to_int(self) -> int | None:
        """Получить идентификатор пригласившего.

        :return: int
        """
        with suppress(StartMessageNotContainReferrerError, UserNotFoundError):
            return await self._origin.to_int()
        return None
