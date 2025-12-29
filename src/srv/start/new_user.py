# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from app_types.async_int_or_none import AsyncIntOrNone


class NewUser(Protocol):
    """Registration of user."""

    async def create(self, referrer_chat_id: AsyncIntOrNone) -> None:
        """Creation.

        :param referrer_chat_id: AsyncIntOrNone
        """
