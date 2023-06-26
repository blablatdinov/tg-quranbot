"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import NamedTuple, Protocol, final

import attrs
from databases import Database


@final
class AyatStructure(NamedTuple):
    """Структура для передачи данных аята."""

    id: int
    sura_num: int
    ayat_num: str


class SuraInterface(Protocol):
    """Интерфейс суры."""

    async def ayats(self, sura_num: int) -> list[AyatStructure]:
        """Получить аяты суры.

        :param sura_num: int
        """


@final
@attrs.define(frozen=True)
class Sura(SuraInterface):
    """Сура."""

    _connection: Database

    async def ayats(self, sura_num: int) -> list[AyatStructure]:
        """Получить аяты по номеру суры.

        :param sura_num: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.ayat_id as id,
                a.sura_id as sura_num,
                a.ayat_number as ayat_num
            FROM ayats a
            WHERE a.sura_id = :sura_num
            ORDER BY a.ayat_id
        """
        records = await self._connection.fetch_all(query, {'sura_num': sura_num})
        return [
            AyatStructure(row['id'], row['sura_num'], row['ayat_num'])
            for row in records
        ]
