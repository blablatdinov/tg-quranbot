from pydantic import BaseModel


class Ayat(BaseModel):
    """Модель аята."""

    sura_num: int
    ayat_num: str
    arab_text: str
    content: str  # noqa: WPS110 wrong variable name
    transliteration: str
    sura_link: str
    audio_telegram_id: str
    link_to_audio_file: str


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
                a.trans as transliteration,
                cf.tg_file_id as audio_telegram_id,
                cf.link_to_file as link_to_audio_file
            FROM content_ayat a
            INNER JOIN content_sura s on a.sura_id = s.id
            INNER JOIN content_file cf on a.audio_id = cf.id
            ORDER BY a.id
            LIMIT 1
        """
        record = await self.connection.fetchrow(query)
        return Ayat(**dict(record))

    async def get_ayats_by_sura_num(self, sura_num: int) -> list[Ayat]:
        """Получить аят по номеру суры.

        :param sura_num: int
        :returns: list[Ayat]
        """
        query = """
            SELECT
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
