# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.runable import Runable


@final
@attrs.define(frozen=True)
class FkRunable(Runable):
    """Fake runable."""

    @override
    async def run(self) -> None:
        """Запуск."""
