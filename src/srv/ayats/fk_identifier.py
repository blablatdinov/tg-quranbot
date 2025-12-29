# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from srv.ayats.ayat_identifier import AyatIdentifier


@final
@attrs.define(frozen=True)
class FkIdentifier(AyatIdentifier):
    """Identifier stub."""

    _id: int
    _sura_num: int
    _ayat_num: str

    @override
    async def ayat_id(self) -> int:
        """Идентификатор.

        :return: int
        """
        return self._id

    @override
    async def sura_num(self) -> int:
        """Номер суры.

        :return: int
        """
        return self._sura_num

    @override
    async def ayat_num(self) -> str:
        """Номер аята.

        :return: str
        """
        return self._ayat_num
