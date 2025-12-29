# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError
from srv.ayats.search_query import AyatNum, SearchQuery, SuraId


@final
@attrs.define(frozen=True)
class ValidatedSearchQuery(SearchQuery):
    """Декоратор, валидирующий запрос для поиска."""

    _origin: SearchQuery

    @override
    def sura(self) -> SuraId:
        """Номер суры.

        :return: int
        :raises SuraNotFoundError: if sura not found
        """
        max_sura_num = 114
        sura_num = self._origin.sura()
        if sura_num not in range(1, max_sura_num + 1):
            raise SuraNotFoundError
        return sura_num

    @override
    def ayat(self) -> AyatNum:
        """Номер аята.

        :return: str
        :raises AyatNotFoundError: if ayat not found
        """
        try:
            ayat_num = int(self._origin.ayat())
        except ValueError as err:
            raise AyatNotFoundError from err
        if ayat_num < 1:
            raise AyatNotFoundError
        return str(ayat_num)
