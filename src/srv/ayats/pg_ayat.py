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

import attrs
from databases import Database

from app_types.intable import AsyncIntable, ThroughAsyncIntable
from app_types.stringable import SupportsStr
from exceptions.content_exceptions import AyatNotFoundError
from services.regular_expression import IntableRegularExpression
from srv.ayats.ayat import Ayat, AyatText, TgFileId
from srv.ayats.ayat_id_by_sura_ayat import AyatIdBySuraAyatNum
from srv.ayats.ayat_identifier import PgAyatIdentifier
from srv.ayats.ayat_link import AyatLink
from srv.ayats.nums_search_query import NumsSearchQuery
from srv.ayats.validated_search_query import ValidatedSearchQuery


@final
@attrs.define(frozen=True)
class PgAyat(Ayat):
    """Аят."""

    _ayat_id: AsyncIntable
    _database: Database

    @classmethod
    async def by_sura_ayat_num(cls, sura_ayat_num: SupportsStr, database: Database) -> Ayat:
        """Конструктор для поиска по номеру суры, аята.

        :param sura_ayat_num: Stringable
        :param database: Database
        :return: Ayat
        """
        return PgAyat(
            AyatIdBySuraAyatNum(
                ValidatedSearchQuery(
                    NumsSearchQuery(sura_ayat_num),
                ),
                database,
            ),
            database,
        )

    @classmethod
    def from_int(cls, ayat_id: int, database) -> Ayat:
        """Конструктор для числа.

        :param ayat_id: int
        :param database: Database
        :return: Ayat
        """
        return PgAyat(ThroughAsyncIntable(ayat_id), database)

    @classmethod
    def from_callback_query(cls, callback_query: SupportsStr, database: Database):
        """Создать аят из данных нажатой inline кнопки.

        :param callback_query: SupportsStr
        :param database: Database
        :return: Ayat
        """
        return PgAyat(
            ThroughAsyncIntable(
                int(IntableRegularExpression(callback_query)),
            ),
            database,
        )

    def identifier(self) -> PgAyatIdentifier:
        """Идентификатор аята.

        :return: int
        """
        return PgAyatIdentifier(self._ayat_id, self._database)

    async def text(self) -> AyatText:
        """Текст аята.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = """
            SELECT
                a.ayat_id AS id,
                a.sura_id AS sura_num,
                s.link AS sura_link,
                a.ayat_number AS ayat_num,
                a.arab_text,
                a.content,
                a.transliteration
            FROM ayats AS a
            INNER JOIN suras AS s ON a.sura_id = s.sura_id
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self._ayat_id.to_int()
        row = await self._database.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError('Аят с id={0} не найден'.format(ayat_id))
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=str(AyatLink(row['sura_link'], row['sura_num'], row['ayat_num'])),
            sura=row['sura_num'],
            ayat=row['ayat_num'],
            arab_text=row['arab_text'],
            content=row['content'],
            transliteration=row['transliteration'],
        )

    async def tg_file_id(self) -> TgFileId:
        """Идентификатор файла в телеграм.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = """
            SELECT cf.telegram_file_id
            FROM ayats AS a
            INNER JOIN files AS cf ON a.audio_id = cf.file_id
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self._ayat_id.to_int()
        row = await self._database.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError('Аят с id={0} не найден'.format(ayat_id))
        return row['telegram_file_id']

    async def file_link(self) -> str:
        """Ссылка на файл.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = """
            SELECT cf.link
            FROM ayats AS a
            INNER JOIN files AS cf ON a.audio_id = cf.file_id
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self._ayat_id.to_int()
        row = await self._database.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError('Аят с id={0} не найден'.format(ayat_id))
        return row['link']
