# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Generic, final, override

import attrs

from app_types.listable import AsyncListable, ListElemT_co


@final
@attrs.define(frozen=True)
class FkAsyncListable(AsyncListable, Generic[ListElemT_co]):
    """Фейковый список."""

    _origin: list[ListElemT_co]

    @override
    async def to_list(self) -> list[ListElemT_co]:
        """Список.

        :return: list[ListElemT]
        """
        return self._origin
