# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, TypeAlias

SuraId: TypeAlias = int
AyatNum: TypeAlias = str


class SearchQuery(Protocol):
    """Интерфейс объекта с запросом для поиска."""

    def sura(self) -> SuraId:
        """Номер суры."""

    def ayat(self) -> AyatNum:
        """Номер аята."""
