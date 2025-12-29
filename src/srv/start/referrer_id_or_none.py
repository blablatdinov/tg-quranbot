# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
