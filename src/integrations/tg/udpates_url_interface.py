# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class UpdatesURLInterface(Protocol):
    """Интерфейс URL запроса для получения уведомлений."""

    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        """
