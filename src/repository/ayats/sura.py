from databases import Database
from pydantic import parse_obj_as

from repository.ayats.schemas import Ayat


class SuraInterface(object):
    """Интерфейс суры."""

    async def ayats(self, sura_num: int):
        """Получить аяты суры.

        :param sura_num: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class Sura(SuraInterface):
    """Сура."""

    def __init__(self, connection: Database):
        self._connection = connection

    async def ayats(self, sura_num: int) -> list[Ayat]:
        """Получить аяты по номеру суры.

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
            ORDER BY a.ayat_id
        """
        records = await self._connection.fetch_all(query, {'sura_num': sura_num})
        return parse_obj_as(list[Ayat], [record._mapping for record in records])  # noqa: WPS437
