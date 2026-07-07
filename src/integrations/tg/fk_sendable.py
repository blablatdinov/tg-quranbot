# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from frozendict import frozendict

from app_types.update import Update
from integrations.tg.sendable import Sendable


@final
@attrs.define(frozen=True)
class FkSendable(Sendable):
    """Фейковый объект для отправки ответов."""

    _origin: list[frozendict]

    @override
    async def send(self, update: Update) -> list[frozendict]:
        """Отправка.

        :param update: Update
        :return: list[str]
        """
        return self._origin
