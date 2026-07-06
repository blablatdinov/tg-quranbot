# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol


class PrayerStts(Protocol):
    """Объект, рассчитывающий данные кнопки для изменения статуса прочитанности намаза."""

    def user_prayer_id(self) -> int:
        """Рассчитать идентификатор времени намаза пользователя."""

    def change_to(self) -> bool:
        """Рассчитать статус времени намаза пользователя."""
