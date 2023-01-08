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
from typing import final
from typing import Protocol

from databases import Database
from pydantic import parse_obj_as

from repository.ayats.schemas import Ayat


class SuraInterface(Protocol):
    """Интерфейс суры."""

    async def ayats(self, sura_num: int):
        """Получить аяты суры.

        :param sura_num: int
        """


class Sura(SuraInterface):
    """Сура."""

    def __init__(self, connection: Database):
        """Конструктор класса.

        :param connection: Database
        """
        self._connection = connection

    async def ayats(self, sura_num: int) -> list[Ayat]:
        """Получить аяты по номеру суры.

        :param sura_num: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.ayat_id as id,
                s.sura_id as sura_num,
                s.link as sura_link,
                a.ayat_number as ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                cf.telegram_file_id as audio_telegram_id,
                cf.link as link_to_audio_file
            FROM ayats a
            INNER JOIN suras s on a.sura_id = s.sura_id
            INNER JOIN files cf on a.audio_id = cf.file_id
            WHERE s.sura_id = :sura_num
            ORDER BY a.ayat_id
        """
        records = await self._connection.fetch_all(query, {'sura_num': sura_num})
        return parse_obj_as(list[Ayat], [record._mapping for record in records])  # noqa: WPS437
