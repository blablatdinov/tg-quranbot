# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Sequence
from typing import Generic, Protocol, TypeVar

ListElemT_co = TypeVar('ListElemT_co', covariant=True)


class AsyncListable(Protocol, Generic[ListElemT_co]):  # type: ignore [misc]
    """Объект, имеющий корутину представляющую его в кач-ве списка."""

    async def to_list(self) -> Sequence[ListElemT_co]:
        """Список."""
