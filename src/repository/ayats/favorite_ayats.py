from asyncpg import Connection
from pydantic import parse_obj_as

from repository.ayats.ayat import Ayat
from repository.schemas import CountResult


class FavoriteAyatRepositoryInterface(object):
    """Интерфейс для работы с хранилищем избранных аятов."""

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        """Метод для аятов в избранном для пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Проверить входит ли аят в избранные.

        :param ayat_id: int
        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def add_to_favorite(self, chat_id: int, ayat_id: int):
        """Добавить аят в избранные.

        :param chat_id: int
        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        """Удалить аят из избранных.

        :param chat_id: int
        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class FavoriteAyatsRepository(FavoriteAyatRepositoryInterface):
    """Класс для работы с хранилищем избранных аятов."""

    def __init__(self, connection: Connection):
        self._connection = connection

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        """Получить избранные аяты.

        :param chat_id: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.id,
                s.number as sura_num,
                s.link as sura_link,
                a.ayat as ayat_num,
                a.arab_text,
                a.content,
                a.trans as transliteration,
                cf.tg_file_id as audio_telegram_id,
                cf.link_to_file as link_to_audio_file
            FROM bot_init_subscriber_favourite_ayats fa
            INNER JOIN content_ayat a ON fa.ayat_id = a.id
            INNER JOIN bot_init_subscriber sub ON fa.subscriber_id = sub.id
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE sub.tg_chat_id = $1
        """
        rows = await self._connection.fetch(query, chat_id)
        return parse_obj_as(list[Ayat], rows)

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Получить аят по номеру суры.

        :param ayat_id: int
        :param chat_id: int
        :returns: bool
        """
        query = """
            SELECT
                count(*)
            FROM bot_init_subscriber_favourite_ayats sub_ayat
            INNER JOIN bot_init_subscriber sub on sub.id = sub_ayat.subscriber_id
            where ayat_id = $1 and sub.tg_chat_id = $2
        """
        row = await self._connection.fetchrow(query, ayat_id, chat_id)
        return bool(CountResult.parse_obj(row).count)

    async def add_to_favorite(self, chat_id: int, ayat_id: int):
        """Добавить аят в избранные.

        :param chat_id: int
        :param ayat_id: int
        """
        query = """
            INSERT INTO bot_init_subscriber_favourite_ayats
            (subscriber_id, ayat_id)
            VALUES
            (
                (SELECT id FROM bot_init_subscriber WHERE tg_chat_id = $1),
                $2
            )
        """
        await self._connection.execute(query, chat_id, ayat_id)

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        """Удалить аят из избранных.

        :param chat_id: int
        :param ayat_id: int
        """
        query = """
            DELETE FROM bot_init_subscriber_favourite_ayats
            WHERE subscriber_id = (SELECT id FROM bot_init_subscriber WHERE tg_chat_id = $1) AND ayat_id = $2
        """
        await self._connection.execute(query, chat_id, ayat_id)
