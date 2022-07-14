from typing import NamedTuple, Optional

from pydantic import BaseModel

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

    def title(self):
        """Заголовок.

        :returns: str
        """
        return '{0}:{1}'.format(self.sura_num, self.ayat_num)


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

    def __init__(self, connection):
        self.connection = connection

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :returns: Ayat
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
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE a.id = $1
        """
        row = await self.connection.fetchrow(query, ayat_id)
        return Ayat(**dict(row))

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
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
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE s.number = $1
        """
        records = await self.connection.fetch(query, sura_num)
        return [
            Ayat(**dict(record))
            for record in records
        ]

    async def search_by_text(self, query: str) -> list[Ayat]:
        """Поиск по тексту.

        :param query: str
        :returns: list[Ayat]
        """
        search_query = '%{0}%'.format(query)
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
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            WHERE a.content ILIKE $1
        """
        rows = await self.connection.fetch(query, search_query)
        return [
            Ayat(**dict(row))
            for row in rows
        ]
