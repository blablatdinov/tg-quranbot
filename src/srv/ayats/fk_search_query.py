# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from srv.ayats.search_query import AyatNum, SearchQuery, SuraId


@final
@attrs.define(frozen=True)
class FkSearchQuery(SearchQuery):
    """Фейковый запрос для поиска аятов."""

    _sura: SuraId
    _ayat: AyatNum

    @override
    def sura(self) -> SuraId:
        """Идентификатор суры.

        :return: SuraId
        """
        return self._sura

    @override
    def ayat(self) -> AyatNum:
        """Номер аята.

        :return: AyatNum
        """
        return self._ayat
