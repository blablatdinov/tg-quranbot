# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.stringable import SupportsStr
from srv.ayats.search_query import AyatNum, SearchQuery, SuraId


@final
@attrs.define(frozen=True)
class NumsSearchQuery(SearchQuery):
    """Запросом для поиска.

    >>> query = NumsSearchQuery('4:5')
    >>> query.sura()
    4
    >>> query.ayat()
    '5'
    """

    _query: SupportsStr

    @override
    def sura(self) -> SuraId:
        """Номер суры.

        :return: int
        """
        return int(str(self._query).split(':')[0])

    @override
    def ayat(self) -> AyatNum:
        """Номер аята.

        :return: str
        """
        return str(self._query).split(':')[1]
