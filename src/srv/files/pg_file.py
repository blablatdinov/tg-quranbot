# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
