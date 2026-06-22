# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid
from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from exceptions.content_exceptions import BotFileNotFoundError
from srv.files.tg_file import FileLink, TgFile, TgFileId


@final
@attrs.define(frozen=True)
class PgFile(TgFile):
    """Объект файла в postgres."""

    _file_id: uuid.UUID
    _pgsql: AsyncEngine

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
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {'file_id': str(self._file_id)})
            row = query_result.fetchone()
        if row is None:
            raise BotFileNotFoundError
        return dict(row)['telegram_file_id']

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
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {'file_id': str(self._file_id)})
            row = query_result.fetchone()
        if row is None:
            raise BotFileNotFoundError
        return dict(row)['link']
