# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.intable import AsyncInt
from exceptions.base_exception import InternalBotError
from srv.files.tg_file import FileLink, TgFile, TgFileId


@final
@attrs.define(frozen=True)
class AyatAudio(TgFile):
    """Аудио аята."""

    _ayat_id: AsyncInt
    _pgsql: AsyncEngine

    @override
    async def tg_file_id(self) -> TgFileId:
        """Получить идентификатор файла.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        :raises TelegramFileIdNotFilledError: идентификатор файла не заполнен
        """
        query = '\n'.join([
            'SELECT cf.file_id',
            'FROM ayats AS a',
            'INNER JOIN files AS cf ON a.ar_audio_id = cf.file_id',
            'WHERE a.ayat_id = :ayat_id',
        ])
        async with self._pgsql.connect() as conn:
            result = await conn.execute(
                text(query),
                {'ayat_id': await self._ayat_id.to_int()},
            )
            row = result.fetchone()
        if row is None:
            msg = 'Аят с id={0} не найден'.format(await self._ayat_id.to_int())
            raise InternalBotError(msg)
        return dict(row._mapping)['file_id']

    @override
    async def file_link(self) -> FileLink:
        """Получить ссылку на файл.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        """
        query = '\n'.join([
            'SELECT cf.link',
            'FROM ayats AS a',
            'INNER JOIN files AS cf ON a.ar_audio_id = cf.file_id',
            'WHERE a.ayat_id = :ayat_id',
        ])
        async with self._pgsql.connect() as conn:
            result = await conn.execute(
                text(query),
                {'ayat_id': await self._ayat_id.to_int()},
            )
            row = result.fetchone()
        if row is None:
            msg = 'Аят с id={0} не найден'.format(await self._ayat_id.to_int())
            raise InternalBotError(msg)
        return dict(row._mapping)['link']
