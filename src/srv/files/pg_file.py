# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import uuid
from typing import final, override

import attrs
from databases import Database

from exceptions.content_exceptions import BotFileNotFoundError
from srv.files.tg_file import FileLink, TgFile, TgFileId


@final
@attrs.define(frozen=True)
class PgFile(TgFile):
    """Объект файла в postgres."""

    _file_id: uuid.UUID
    _pgsql: Database

    @override
    async def tg_file_id(self) -> TgFileId:
        """Идентификатор файла в телеграм.

        :return: str
        :raises BotFileNotFoundError: файл не найден
        """
        query = '\n'.join([
            'SELECT telegram_file_id',
            'FROM files',
            'WHERE file_id = :file_id',
        ])
        row = await self._pgsql.fetch_one(query, {'file_id': str(self._file_id)})
        if not row:
            raise BotFileNotFoundError
        return row['telegram_file_id']

    @override
    async def file_link(self) -> FileLink:
        """Ссылка на файл.

        :return: str
        :raises BotFileNotFoundError: файл не найден
        """
        query = '\n'.join([
            'SELECT link',
            'FROM files',
            'WHERE file_id = :file_id',
        ])
        row = await self._pgsql.fetch_one(query, {'file_id': str(self._file_id)})
        if not row:
            raise BotFileNotFoundError
        return row['link']
