from databases import Database
from pydantic import parse_obj_as

from exceptions.base_exception import InternalBotError
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
        """
        rows = await self._connection.fetch_all(query, {'chat_id': chat_id})
        return parse_obj_as(list[Ayat], [row._mapping for row in rows])  # noqa: WPS437

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Получить аят по номеру суры.

        :param ayat_id: int
        :param chat_id: int
        :returns: bool
        """
        query = """
            SELECT
                COUNT(*)
            FROM favorite_ayats fa
            INNER JOIN users u ON u.chat_id = fa.user_id
            WHERE fa.ayat_id = :ayat_id AND u.chat_id = :chat_id
        """
        row = await self._connection.fetch_val(query, {'ayat_id': ayat_id, 'chat_id': chat_id})
        return bool(CountResult.parse_obj(row._mapping).count)  # noqa: WPS437

    async def add_to_favorite(self, chat_id: int, ayat_id: int):
        """Добавить аят в избранные.

        :param chat_id: int
        :param ayat_id: int
        """
        query = """
            INSERT INTO favorite_ayats
            (user_id, ayat_id)
            VALUES
            (:chat_id, :ayat_id)
        """
        await self._connection.execute(query, {'chat_id': chat_id, 'ayat_id': ayat_id})

    async def remove_from_favorite(self, chat_id: int, ayat_id: int):
        """Удалить аят из избранных.

        :param chat_id: int
        :param ayat_id: int
        """
        query = """
            DELETE FROM favorite_ayats
            WHERE user_id = :chat_id AND ayat_id = :ayat_id
        """
        await self._connection.execute(query, {'chat_id': chat_id, 'ayat_id': ayat_id})
