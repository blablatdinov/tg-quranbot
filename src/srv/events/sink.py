# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from frozendict import frozendict


class Sink(Protocol):
    """Интерфейс отправщика событий."""

    async def send(self, queue_name: str, event_data: frozendict, event_name: str, version: int) -> None:
        """Отправить событие.

        :param queue_name: str
        :param event_data: dict
        :param event_name: str
        :param version: int
        """
