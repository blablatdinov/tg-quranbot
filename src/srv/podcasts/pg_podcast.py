from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncInt
from exceptions.base_exception import InternalBotError
from exceptions.content_exceptions import TelegramFileIdNotFilledError
from srv.files.tg_file import FileLink, TgFileId
from srv.podcasts.podcast import Podcast


@final
@attrs.define(frozen=True)
@elegant
class PgPodcast(Podcast):
    """Объект подкаста."""

    _podcast_id: AsyncInt
    _pgsql: Database

    @override
    async def podcast_id(self) -> int:
        """Идентификатор подкаста.

        :return: int
        """
        return await self._podcast_id.to_int()

    @override
    async def tg_file_id(self) -> TgFileId:
        """Получить идентификатор файла.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        :raises TelegramFileIdNotFilledError: идентификатор файла не заполнен
        """
        query = '\n'.join([
            'SELECT f.telegram_file_id',
            'FROM podcasts AS p',
            'INNER JOIN files AS f ON p.file_id = f.file_id',
            'WHERE p.podcast_id = :podcast_id',
        ])
        row = await self._pgsql.fetch_one(
            query,
            {'podcast_id': await self._podcast_id.to_int()},
        )
        if not row:
            msg = 'Подкасты не найдены'
            raise InternalBotError(msg)
        if not row['telegram_file_id']:
            raise TelegramFileIdNotFilledError
        return row['telegram_file_id']

    @override
    async def file_link(self) -> FileLink:
        """Получить ссылку на файл.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        """
        query = '\n'.join([
            'SELECT f.link',
            'FROM podcasts AS p',
            'INNER JOIN files AS f ON p.file_id = f.file_id',
            'WHERE p.podcast_id = :podcast_id',
        ])
        row = await self._pgsql.fetch_one(
            query,
            {'podcast_id': await self._podcast_id.to_int()},
        )
        if not row:
            msg = 'Подкасты не найдены'
            raise InternalBotError(msg)
        return row['link']
