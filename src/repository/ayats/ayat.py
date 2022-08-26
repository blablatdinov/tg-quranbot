from typing import NamedTuple, Optional

from databases import Database
from pydantic import BaseModel, parse_obj_as

from exceptions.base_exception import InternalBotError
from repository.ayats.neighbor_ayats import AyatShort


class AyatNeighbors(NamedTuple):
    """DTO для передачи соседних аятов."""

    left: Optional[AyatShort]
    right: Optional[AyatShort]


class Ayat(BaseModel):
    """Модель аята."""

    id: int
    sura_num: int
    ayat_num: str
    arab_text: str
    content: str  # noqa: WPS110 wrong variable name
    transliteration: str
    sura_link: str
    audio_telegram_id: str
    link_to_audio_file: str
    left_neighbor: Optional[AyatShort]
    right_neighbor: Optional[AyatShort]

    def __str__(self) -> str:
        """Отформатировать аят для сообщения.

        :returns: str
        """
        link = 'https://umma.ru{sura_link}'.format(sura_link=self.sura_link)
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=link,
            sura=self.sura_num,
            ayat=self.ayat_num,
            arab_text=self.arab_text,
            content=self.content,
            transliteration=self.transliteration,
        )

    def find_neighbors(self) -> AyatNeighbors:
        """Возвращает соседние аяты.

        :returns: AyatNeighbors
        """
        return AyatNeighbors(left=self.left_neighbor, right=self.right_neighbor)

    def title(self) -> str:
        """Заголовок.

        :returns: str
        """
        return '{0}:{1}'.format(self.sura_num, self.ayat_num)

    def get_short(self) -> AyatShort:
        """Трансформировать в короткую версию.

        :returns: AyatShort
        """
        return AyatShort(id=self.id, ayat_num=self.ayat_num, sura_num=self.sura_num)


class AyatRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_ayat_by_sura_ayat_num(self, sura_num: str, ayat_num: str) -> Ayat:
        """Получить аят по номеру суры и аята.

        :param sura_num: int
        :param ayat_num: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def search_by_text(self, query: str):
        """Поиск по тексту.

        :param query: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatRepository(AyatRepositoryInterface):
    """Интерфейс репозитория для работы с административными сообщениями."""

    def __init__(self, connection: Database):
        self.connection = connection

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :returns: Ayat
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
