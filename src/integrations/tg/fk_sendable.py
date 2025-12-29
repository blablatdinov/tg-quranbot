# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.sendable import Sendable


@final
@attrs.define(frozen=True)
class FkSendable(Sendable):
    """Фейковый объект для отправки ответов."""

    _origin: list[dict]

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[str]
        """
        return self._origin
