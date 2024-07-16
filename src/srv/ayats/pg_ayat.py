# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
from databases import Database
from eljson.json import Json

from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from app_types.stringable import SupportsStr
from exceptions.content_exceptions import AyatNotFoundError
from services.instable_regex import IntableRegex
from srv.ayats.ayat import Ayat, AyatText
from srv.ayats.ayat_id_by_public_id import AyatIdByPublicId
from srv.ayats.ayat_id_by_sura_ayat_num import AyatIdBySuraAyatNum
from srv.ayats.ayat_link import AyatLink
from srv.ayats.nums_search_query import NumsSearchQuery
from srv.ayats.pg_ayat_identifier import PgAyatIdentifier
from srv.ayats.validated_search_query import ValidatedSearchQuery
from srv.files.pg_file import PgFile
from srv.files.tg_file import TgFile


@final
@attrs.define(frozen=True)
class PgAyat(Ayat):  # noqa: WPS214. This class contain 4 secondary ctor and 4 method
    """Аят."""

    _ayat_id: AsyncInt
    _pgsql: Database

    @classmethod
    def by_sura_ayat_num(cls, sura_ayat_num: SupportsStr, database: Database) -> Ayat:
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
    def from_int(cls, ayat_id: int, database: Database) -> Ayat:
        """Конструктор для числа.

        :param ayat_id: int
        :param database: Database
        :return: Ayat
        """
        return PgAyat(FkAsyncInt(ayat_id), database)

    @classmethod
    def from_callback_query(cls, callback_query: SupportsStr, database: Database) -> Ayat:
        """Создать аят из данных нажатой inline кнопки.

        :param callback_query: SupportsStr
        :param database: Database
        :return: Ayat
        """
        return PgAyat(
            FkAsyncInt(
                int(IntableRegex(callback_query)),
            ),
            database,
        )

    @classmethod
    def ayat_changed_event_ctor(cls, event_body: Json, pgsql: Database) -> Ayat:
        """Конструктор для события изменения аята.

        :param event_body: Json
        :param pgsql: Database
        :return: Ayat
        """
        return cls(
            AyatIdByPublicId(event_body.path('$.data.public_id')[0], pgsql),
            pgsql,
        )

    @override
    def identifier(self) -> PgAyatIdentifier:
        """Идентификатор аята.

        :return: int
        """
        return PgAyatIdentifier(self._ayat_id, self._pgsql)

    @override
    async def to_str(self) -> AyatText:
        """Текст аята.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = '\n'.join([
            'SELECT',
            '    a.ayat_id AS id,',
            '    a.sura_id AS sura_num,',
            '    s.link AS sura_link,',
            '    a.ayat_number AS ayat_num,',
            '    a.arab_text,',
            '    a.content,',
            '    a.transliteration',
            'FROM ayats AS a',
            'INNER JOIN suras AS s ON a.sura_id = s.sura_id',
            'WHERE a.ayat_id = :ayat_id',
        ])
        ayat_id = await self._ayat_id.to_int()
        row = await self._pgsql.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            msg = 'Аят с id={0} не найден'.format(ayat_id)
            raise AyatNotFoundError(msg)
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=str(AyatLink(row['sura_link'], row['sura_num'], row['ayat_num'])),
            sura=row['sura_num'],
            ayat=row['ayat_num'],
            arab_text=row['arab_text'],
            content=row['content'],
            transliteration=row['transliteration'],
        )

    @override
    async def audio(self) -> TgFile:
        """Получить аудио аята.

        :return: File
        :raises AyatNotFoundError: если аят не найден
        """
        query = '\n'.join([
            'SELECT cf.file_id',
            'FROM ayats AS a',
            'INNER JOIN files AS cf ON a.audio_id = cf.file_id',
            'WHERE a.ayat_id = :ayat_id',
        ])
        ayat_id = await self._ayat_id.to_int()
        row = await self._pgsql.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            msg = 'Аят с id={0} не найден'.format(ayat_id)
            raise AyatNotFoundError(msg)
        return PgFile(row['file_id'], self._pgsql)

    @override
    async def change(self, event_body: Json) -> None:
        """Изменить содержимое аята.

        :param event_body: Json
        """
        query = '\n'.join([
            'UPDATE ayats',
            'SET',
            '    day = :day,',
            '    audio_id = :audio_id,',
            '    ayat_number = :ayat_number,',
            '    content = :content,',
            '    arab_text = :arab_text,',
            '    transliteration = :transliteration',
            'WHERE ayat_id = :ayat_id',
        ])
        await self._pgsql.execute(query, {
            'ayat_id': await self._ayat_id.to_int(),
            'day': event_body.path('$.data.day')[0],
            'audio_id': event_body.path('$.data.audio_id')[0],
            'ayat_number': event_body.path('$.data.ayat_number')[0],
            'content': event_body.path('$.data.content')[0],
            'arab_text': event_body.path('$.data.arab_text')[0],
            'transliteration': event_body.path('$.data.transliteration')[0],
        })
