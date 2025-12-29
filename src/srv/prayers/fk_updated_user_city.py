# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from srv.prayers.updated_user_city import UpdatedUserCity


@final
@attrs.define(frozen=True)
class FkUpdateUserCity(UpdatedUserCity):
    """Стаб для обновления города."""

    @override
    async def update(self) -> None:
        """Обновление."""
