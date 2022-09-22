from databases import Database

from exceptions.base_exception import InternalBotError


class RandomPodcastInterface(object):
    """Интерфейс подкаста.

    https://www.yegor256.com/2014/12/01/orm-offensive-anti-pattern.html
    """

    async def audio_telegram_id(self) -> str:
        """Получить идентификатор файла.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def link_to_audio_file(self) -> str:
        """Получить ссылку на файл.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class RandomPodcast(RandomPodcastInterface):
    """Объект подкаста."""

    def __init__(self, connection: Database):
        self._connection = connection

    async def audio_telegram_id(self):
        """Получить идентификатор файла.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        """
        query = """
            SELECT
                f.telegram_file_id
            FROM podcasts p
            INNER JOIN files f ON p.file_id = f.file_id
            ORDER BY RANDOM()
            LIMIT 1
        """
        row = await self._connection.fetch_one(query)
        if not row:
            raise InternalBotError('Подкасты не найдены')
        return row._mapping['telegram_file_id']  # noqa: WPS437

    async def link_to_audio_file(self):
        """Получить ссылку на файл.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        """
        query = """
            SELECT
                f.link
            FROM podcasts p
            INNER JOIN files f ON p.file_id = f.file_id
            ORDER BY RANDOM()
            LIMIT 1
        """
        row = await self._connection.fetch_one(query)
        if not row:
            raise InternalBotError('Подкасты не найдены')
        return row._mapping['link']  # noqa: WPS437
