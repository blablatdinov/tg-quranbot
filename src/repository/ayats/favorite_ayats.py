from databases import Database
from loguru import logger
from pydantic import parse_obj_as

from repository.ayats.schemas import Ayat


class FavoriteAyatRepositoryInterface(object):
    """Интерфейс для работы с хранилищем избранных аятов."""

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        """Метод для аятов в избранном для пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_favorite(self, ayat_id: int) -> Ayat:
        """Метод для аятов в избранном для пользователя.

        :param ayat_id: int
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


class FavoriteAyatsRepository(FavoriteAyatRepositoryInterface):
    """Класс для работы с хранилищем избранных аятов."""

    def __init__(self, connection: Database):
        self._connection = connection

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        """Получить избранные аяты.

        :param chat_id: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.ayat_id AS id,
                s.sura_id AS sura_num,
                s.link AS sura_link,
                a.ayat_number AS ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                f.file_id AS audio_telegram_id,
                f.link AS link_to_audio_file
            FROM favorite_ayats fa
            INNER JOIN ayats a ON fa.ayat_id = a.ayat_id
            INNER JOIN users u ON fa.user_id = u.chat_id
            INNER JOIN suras s ON a.sura_id = s.sura_id
            INNER JOIN files f ON a.audio_id = f.file_id
            WHERE u.chat_id = :chat_id
            ORDER BY a.ayat_id
        """
        rows = await self._connection.fetch_all(query, {'chat_id': chat_id})
        return parse_obj_as(list[Ayat], [row._mapping for row in rows])  # noqa: WPS437

    async def get_favorite(self, ayat_id: int) -> Ayat:
        """Метод для аятов в избранном для пользователя.

        :param ayat_id: int
        """
        query = """
            SELECT
                a.ayat_id AS id,
                s.sura_id AS sura_num,
                s.link AS sura_link,
                a.ayat_number AS ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                f.file_id AS audio_telegram_id,
                f.link AS link_to_audio_file
            FROM favorite_ayats fa
            INNER JOIN ayats a ON fa.ayat_id = a.ayat_id
            INNER JOIN users u ON fa.user_id = u.chat_id
            INNER JOIN suras s ON a.sura_id = s.sura_id
            INNER JOIN files f ON a.audio_id = f.file_id
            WHERE a.ayat_id = :ayat_id
        """
        row = await self._connection.fetch_one(query, {'ayat_id': ayat_id})
        return Ayat.parse_obj(row._mapping)

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Получить аят по номеру суры.

        :param ayat_id: int
        :param chat_id: int
        :returns: bool
        """
        logger.debug('Check ayat <{0}> is favorite for user <{1}>...'.format(ayat_id, chat_id))
        query = """
            SELECT
                COUNT(*)
            FROM favorite_ayats fa
            INNER JOIN users u ON u.chat_id = fa.user_id
            WHERE fa.ayat_id = :ayat_id AND u.chat_id = :chat_id
        """
        count = await self._connection.fetch_val(query, {'ayat_id': ayat_id, 'chat_id': chat_id})
        logger.debug('Ayat <{0}> is favorite for user <{1}> result: {2}'.format(ayat_id, chat_id, bool(count)))
        return bool(count)
