from pydantic import BaseModel


class Ayat(BaseModel):
    """Модель аята."""

    sura_num: int
    ayat_num: str
    arab_text: str
    content: str  # noqa: WPS110 wrong variable name
    transliteration: str
    sura_link: str


class AyatRepositoryInterface(object):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, ayat_id: int) -> Ayat:
        """Метод для получения аята по идентификатору.

        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def first(self) -> Ayat:
        """Метод для получения первого аята.

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
        :raises: NotImplementedError if not implemented
        """
        pass  # noqa: WPS420

    async def first(self) -> Ayat:
        """Метод для получения первого аята.

        :raises: NotImplementedError if not implemented
        :returns: Ayat
        """
        query = """
            SELECT
                s.number as sura_num,
                s.link as sura_link,
                a.ayat as ayat_num,
                a.arab_text,
                a.content,
                a.trans as transliteration
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            ORDER BY a.id
            LIMIT 1
        """
        record = await self.connection.fetchrow(query)
        return Ayat(**dict(record))
