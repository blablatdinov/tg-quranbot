from databases import Database
from pydantic import parse_obj_as

from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import AyatShort


class NeighborAyatsRepositoryInterface(object):
    """Интерфейс для работы с соседними аятами в хранилище."""

    async def left_neighbor(self) -> AyatShort:
        """Левый аят.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def right_neighbor(self) -> AyatShort:
        """Правый аят.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class FavoriteNeighborAyats(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    def __init__(
        self,
        ayat_id: int,
        chat_id: int,
        favorite_ayats_repo: FavoriteAyatRepositoryInterface,
    ) -> None:
        self._chat_id = chat_id
        self._ayat_id = ayat_id
        self._favorite_ayats_repo = favorite_ayats_repo

    async def left_neighbor(self) -> AyatShort:
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_index, ayat in enumerate(fayats):
            if ayat.id == self._ayat_id and ayat_index == 0:
                raise AyatNotFoundError
            elif ayat.id == self._ayat_id:
                return fayats[ayat_index - 1].get_short()
        raise AyatNotFoundError

    async def right_neighbor(self) -> AyatShort:
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_index, ayat in enumerate(fayats):
            if ayat.id == self._ayat_id and ayat_index + 1 == len(fayats):
                raise AyatNotFoundError
            elif ayat.id == self._ayat_id:
                return fayats[ayat_index + 1].get_short()
        raise AyatNotFoundError


class NeighborAyats(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    def __init__(self, connection: Database, ayat_id):
        self._connection = connection
        self._ayat_id = ayat_id

    async def left_neighbor(self):
        query = """
            SELECT
                ayats.ayat_id as id,
                ayats.ayat_number as ayat_num,
                ayats.sura_id as sura_num
            FROM ayats
            WHERE ayats.ayat_id = :ayat_id
        """
        row = await self._connection.fetch_one(query, {'ayat_id': self._ayat_id - 1})
        if not row:
            raise AyatNotFoundError
        return parse_obj_as(AyatShort, row._mapping)

    async def right_neighbor(self):
        query = """
            SELECT
                ayats.ayat_id as id,
                ayats.ayat_number as ayat_num,
                ayats.sura_id as sura_num
            FROM ayats
            WHERE ayats.ayat_id = :ayat_id
        """
        row = await self._connection.fetch_one(query, {'ayat_id': self._ayat_id + 1})
        if not row:
            raise AyatNotFoundError
        return parse_obj_as(AyatShort, row._mapping)


class TextSearchNeighborAyatsRepository(NeighborAyatsRepositoryInterface):
    """Класс для работы с сосденими аятами, при текстовом поиске."""

    def __init__(self, connection: Database, query: str):
        self.connection = connection
        self._query = query

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
                     a.ayat_id AS id,
                     a.ayat_number AS ayat_num,
                     cs.sura_id AS sura_num,
                     lag(a.ayat_id) OVER (ORDER BY a.ayat_id ASC) AS prev,
                     lead(a.ayat_id) OVER (ORDER BY a.ayat_id ASC) AS next
                FROM (
                    SELECT ayats.* FROM ayats
                    WHERE ayats.content ILIKE :query
                ) a
                INNER JOIN suras cs ON cs.sura_id = a.sura_id
            ) x
            WHERE :ayat_id IN (id, prev, next)
        """
        rows = await self.connection.fetch_all(
            query,
            {'ayat_id': ayat_id, 'query': '%{0}%'.format(self._query)},
        )
        return parse_obj_as(list[AyatShort], [row._mapping for row in rows])  # noqa: WPS437
