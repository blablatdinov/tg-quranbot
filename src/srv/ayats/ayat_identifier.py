# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, TypeAlias

from srv.ayats.search_query import AyatNum, SuraId

AyatId: TypeAlias = int


class AyatIdentifier(Protocol):
    """Информация для идентификации аята."""

    async def ayat_id(self) -> AyatId:
        """Идентификатор в хранилище."""

    async def sura_num(self) -> SuraId:
        """Номер суры."""

    async def ayat_num(self) -> AyatNum:
        """Номер аята."""
