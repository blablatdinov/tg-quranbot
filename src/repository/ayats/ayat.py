from typing import NamedTuple, Optional, Protocol

from databases import Database
from pydantic import parse_obj_as

from exceptions.base_exception import InternalBotError
from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.schemas import Ayat, AyatShort


class AyatNeighbors(NamedTuple):
    """DTO для передачи соседних аятов."""

    left: Optional[AyatShort]
    right: Optional[AyatShort]


class AyatRepositoryInterface(Protocol):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        """

    async def first(self) -> Ayat:
        """Получить первый аят."""

    async def get_ayat_by_sura_ayat_num(self, sura_num: str, ayat_num: str) -> Ayat:
        """Получить аят по номеру суры и аята.

        :param sura_num: int
        :param ayat_num: int
        """

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
        """

    async def search_by_text(self, query: str) -> list[Ayat]:
        """Поиск по тексту.

        :param query: str
        """


class AyatRepository(AyatRepositoryInterface):
    """Интерфейс репозитория для работы с административными сообщениями."""

    def __init__(self, connection: Database):
        """Конструктор класса.

        :param connection: Database
        """
        self.connection = connection

    async def first(self) -> Ayat:
        """Получить первый аят.

        :return: Ayat
        :raises AyatNotFoundError: if ayat not found
        """
        query = """
            SELECT
                a.ayat_id as id,
                s.sura_id as sura_num,
                s.link as sura_link,
                a.ayat_number as ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                cf.telegram_file_id as audio_telegram_id,
                cf.link as link_to_audio_file
            FROM ayats a
            INNER JOIN suras s on a.sura_id = s.sura_id
            INNER JOIN files cf on a.audio_id = cf.file_id
            ORDER BY a.ayat_id
            LIMIT 1
        """
        row = await self.connection.fetch_one(query)
        if not row:
            raise AyatNotFoundError
        return Ayat.parse_obj(row._mapping)  # noqa: WPS437

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :returns: Ayat
        :raises InternalBotError: возбуждается если аят с переданным идентификатором не найден
        """
        query = """
            SELECT
                a.ayat_id as id,
                s.sura_id as sura_num,
                s.link as sura_link,
                a.ayat_number as ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                cf.telegram_file_id as audio_telegram_id,
                cf.link as link_to_audio_file
            FROM ayats a
            INNER JOIN suras s on a.sura_id = s.sura_id
            INNER JOIN files cf on a.audio_id = cf.file_id
            WHERE a.ayat_id = :ayat_id
        """
        row = await self.connection.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise InternalBotError('Аят с id={0} не найден'.format(ayat_id))
        return Ayat.parse_obj(row._mapping)  # noqa: WPS437

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
                a.ayat_id as id,
                s.sura_id as sura_num,
                s.link as sura_link,
                a.ayat_number as ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                cf.telegram_file_id as audio_telegram_id,
                cf.link as link_to_audio_file
            FROM ayats a
            INNER JOIN suras s on a.sura_id = s.sura_id
            INNER JOIN files cf on a.audio_id = cf.file_id
            WHERE s.sura_id = :sura_num
        """
        records = await self.connection.fetch_all(query, {'sura_num': sura_num})
        return parse_obj_as(list[Ayat], [record._mapping for record in records])  # noqa: WPS437

    async def search_by_text(self, query: str) -> list[Ayat]:
        """Поиск по тексту.

        :param query: str
        :returns: list[Ayat]
        """
        search_query = '%{0}%'.format(query)
        query = """
            SELECT
                a.ayat_id as id,
                s.sura_id as sura_num,
                s.link as sura_link,
                a.ayat_number as ayat_num,
                a.arab_text,
                a.content,
                a.transliteration,
                cf.telegram_file_id as audio_telegram_id,
                cf.link as link_to_audio_file
            FROM ayats a
            INNER JOIN suras s on a.sura_id = s.sura_id
            INNER JOIN files cf on a.audio_id = cf.file_id
            WHERE a.content ILIKE :search_query
            ORDER BY a.ayat_id
        """
        rows = await self.connection.fetch_all(query, {'search_query': search_query})
        return parse_obj_as(list[Ayat], [record._mapping for record in rows])  # noqa: WPS437

    async def get_ayat_by_sura_ayat_num(self, sura_num: str, ayat_num: str) -> Ayat:
        """Получить аят по номеру суры и аята.

        :param sura_num: int
        :param ayat_num: int
        :raises NotImplementedError: not implemented
        """
        raise NotImplementedError
