# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, TypeAlias, final, override

import attrs

ChatId: TypeAlias = SupportsInt


@final
@attrs.define(frozen=True)
class FkChatId(ChatId):
    """Фейк идентификатора чата."""

    _origin: int

    @override
    def __int__(self) -> int:
        """Числовое представление.

        :return: int
        """
        return self._origin
