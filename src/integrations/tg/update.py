# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.stringable import SupportsStr
from app_types.update import Update


@final
@attrs.define(frozen=True)
class TgUpdate(Update):
    """Объект обновления от телеграмма."""

    _update_dict: dict

    @classmethod
    def str_ctor(cls, raw_update: SupportsStr) -> Update:
        """Конструктор для строки.

        :param raw_update: SupportsStr
        :return: TgUpdate
        """
        return cls(ujson.loads(str(raw_update)))  # noqa: PEO102

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return ujson.dumps(self._update_dict)

    @override
    def asdict(self) -> dict:
        """Словарь.

        # TODO #360:30min возможно стоит возвращать валидированный dict: return self.parsed().dict().
        #  Подумать насколько тут необходима валидация

        :return: dict
        """
        return self._update_dict
