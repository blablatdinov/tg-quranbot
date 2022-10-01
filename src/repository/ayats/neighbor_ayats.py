from databases import Database
from pydantic import parse_obj_as

from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import AyatShort
from services.ayats.ayat_text_search_query import AyatTextSearchQueryInterface


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
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_index, ayat in enumerate(fayats):
            if ayat.id == self._ayat_id and ayat_index == 0:
                raise AyatNotFoundError
            elif ayat.id == self._ayat_id:
                return fayats[ayat_index - 1].get_short()
        raise AyatNotFoundError

    async def right_neighbor(self) -> AyatShort:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
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
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
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
        return parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437

    async def right_neighbor(self):
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
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
        return parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437


class TextSearchNeighborAyatsRepository(NeighborAyatsRepositoryInterface):
    """Класс для работы с сосденими аятами, при текстовом поиске."""

    _search_sql_query = """
        SELECT
            ayats.ayat_id as id,
            ayats.ayat_number as ayat_num,
            ayats.sura_id as sura_num
        FROM ayats
        WHERE content ILIKE :search_query
        ORDER BY ayat_id
    """

    def __init__(self, connection: Database, ayat_id, query: AyatTextSearchQueryInterface):
        self._connection = connection
        self._ayat_id = ayat_id
        self._query = query

    async def left_neighbor(self):
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._connection.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[1:], start=1):
            ayat = parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437
            if ayat.id == self._ayat_id:
                try:
                    return parse_obj_as(AyatShort, rows[idx - 1]._mapping)  # noqa: WPS437
                except IndexError as err:
                    raise AyatNotFoundError from err
        raise AyatNotFoundError

    async def right_neighbor(self):
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._connection.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[:-1]):
            ayat = parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437
            if ayat.id == self._ayat_id:
                try:
                    return parse_obj_as(AyatShort, rows[idx + 1]._mapping)  # noqa: WPS437
                except IndexError as err:
                    raise AyatNotFoundError from err
        raise AyatNotFoundError
