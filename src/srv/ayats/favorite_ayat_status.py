# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol

from srv.ayats.ayat_identifier import AyatId


class FavoriteAyatStatus(Protocol):
    """Пользовательский ввод статуса аята в избранном."""

    def ayat_id(self) -> AyatId:
        """Идентификатор аята."""

    def change_to(self) -> bool:
        """Целевое значение."""
