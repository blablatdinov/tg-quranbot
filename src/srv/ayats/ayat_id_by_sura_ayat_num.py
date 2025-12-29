# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.intable import AsyncInt
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_identifier import AyatId
from srv.ayats.search_query import SearchQuery


@final
@attrs.define(frozen=True)
class AyatIdBySuraAyatNum(AsyncInt):
    """Поиск аятов по номеру суры, аята."""

    _query: SearchQuery
    _pgsql: Database

    @override
    async def to_int(self) -> AyatId:
        """Числовое представление.

        :return: int
        :raises AyatNotFoundError: если аят не найден
        """
        query = '\n'.join([
            'SELECT ayat_id FROM ayats',
            'WHERE',
            '    sura_id = :sura_id',
            '    AND (',
            '        ayat_number LIKE :ayat_num_str',
            '        OR ayat_number LIKE :ayat_comma_prefix',
            '        OR ayat_number LIKE :ayat_comma_postfix',
            '        OR (',
            "            CAST(SUBSTRING(ayat_number FROM '^[0-9]+') AS INTEGER) <= :ayat_num",
            "            AND CAST(SUBSTRING(ayat_number FROM '[0-9]+$') AS INTEGER) >= :ayat_num",
            '        )',
            '    )',
        ])
        row = await self._pgsql.fetch_one(query, {
            'sura_id': self._query.sura(),
            'ayat_comma_prefix': '%,{0}'.format(self._query.ayat()),
            'ayat_comma_postfix': '%{0},'.format(self._query.ayat()),
            'ayat_num': int(self._query.ayat()),
            'ayat_num_str': self._query.ayat(),
        })
        if not row:
            raise AyatNotFoundError
        return row['ayat_id']
