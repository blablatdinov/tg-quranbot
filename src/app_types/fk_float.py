# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsFloat, final, override

import attrs


@attrs.define(frozen=True)
@final
class FkFloat(SupportsFloat):
    """Фейк для интерфейса SupportsFloat."""

    _origin: float

    @override
    def __float__(self) -> float:  # noqa: PEO602. fake object
        return self._origin
