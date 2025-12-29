# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from srv.users.new_user import NewUser


@final
@attrs.define(frozen=True)
class FkNewUser(NewUser):
    """Фейк нового пользователя."""

    @override
    async def create(self) -> None:
        """Создание."""
