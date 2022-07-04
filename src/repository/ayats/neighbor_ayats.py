from pydantic import BaseModel


class AyatShort(BaseModel):
    """Короткая модель аята."""

    id: int
    sura_num: int
    ayat_num: str


class NeighborAyatsRepositoryInterface(object):
    """Интерфейс для работы с соседними аятами в хранилище."""

    async def get_ayat_neighbors(self, ayat_id: int) -> list[AyatShort]:
        """Достать соседние аяты.

        :param ayat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class FavoriteAyatsNeighborRepository(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    def __init__(self, connection, chat_id: int):
        self.connection = connection
        self.chat_id = chat_id

    async def get_ayat_neighbors(self, ayat_id: int) -> list[AyatShort]:
        """Получить соседние аяты.

        :param ayat_id: int
        :returns: list[AyatShort]
        """
        query = """
            SELECT
                *
            FROM (
                SELECT
                     a.id,
                     a.ayat as ayat_num,
                     cs.number as sura_num,
                     lag(a.id) OVER (ORDER BY a.id ASC) AS prev,
                     lead(a.id) OVER (ORDER BY a.id ASC) AS next
                FROM (
                    SELECT content_ayat.* FROM content_ayat
                    INNER JOIN bot_init_subscriber_favourite_ayats bisfa on content_ayat.id = bisfa.ayat_id
                    INNER JOIN bot_init_subscriber sub on bisfa.subscriber_id = sub.id
                    WHERE sub.tg_chat_id = $2
                ) a
                INNER JOIN content_sura cs on cs.id = a.sura_id
                ) x
            WHERE $1 IN (id, prev, next)
        """
        rows = await self.connection.fetch(query, ayat_id, self.chat_id)
        return [
            AyatShort(**dict(row))
            for row in rows
        ]


class NeighborAyatsRepository(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    def __init__(self, connection):
        self.connection = connection

    async def get_ayat_neighbors(self, ayat_id: int) -> list[AyatShort]:
        """Получить соседние аяты.

        :param ayat_id: int
        :returns: list[AyatShort]
        """
        query = """
            SELECT
                *
            FROM (
                SELECT
                    a.id,
                    a.ayat as ayat_num,
                    cs.number as sura_num,
                    lag(a.id) OVER (ORDER BY a.id ASC) AS prev,
                    lead(a.id) OVER (ORDER BY a.id ASC) AS next
                FROM content_ayat a
                INNER JOIN content_sura cs on cs.id = a.sura_id
            ) x
            WHERE $1 IN (id, prev, next)
        """
        rows = await self.connection.fetch(query, ayat_id)
        return [
            AyatShort(**dict(row))
            for row in rows
        ]
