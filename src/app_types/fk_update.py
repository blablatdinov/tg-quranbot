# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.stringable import SupportsStr
from app_types.update import Update


@final
@attrs.define(frozen=True)
class FkUpdate(Update):
    """Подделка обновления."""

    _raw: SupportsStr

    @classmethod
    def empty_ctor(cls) -> Update:
        """Ctor.

        :return: Update
        """
        return cls('{}')  # noqa: P103. Empty json

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return str(self._raw)

    @override
    def asdict(self) -> dict:
        """Словарь.

        :return: dict
        """
        return ujson.loads(str(self._raw))
