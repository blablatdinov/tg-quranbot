# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from srv.events.sink import Sink


@final
@attrs.define(frozen=True)
class FkSink(Sink):
    """Фейковый слив для событий."""

    @override
    async def send(self, queue_name: str, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param queue_name: str
        :param event_data: dict
        :param event_name: str
        :param version: int
        """
