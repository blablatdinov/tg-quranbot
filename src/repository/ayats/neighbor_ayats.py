from typing import Protocol

from databases import Database
from pydantic import parse_obj_as

from exceptions.base_exception import BaseAppError
from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import AyatShort
from services.ayats.ayat_text_search_query import AyatTextSearchQueryInterface


class NeighborAyatsRepositoryInterface(Protocol):
    """Интерфейс для работы с соседними аятами в хранилище."""

    async def left_neighbor(self) -> AyatShort:
        """Левый аят."""

    async def right_neighbor(self) -> AyatShort:
        """Правый аят."""

    async def page(self) -> str:
        """Информация о странице."""


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

    async def page(self) -> str:
        """Информация о странице.

        :return: str
        :raises BaseAppError: if page not generated
        """
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_idx, ayat in enumerate(fayats, start=1):
            if self._ayat_id == 1:
                return 'стр. 1/{0}'.format(len(fayats))
            elif ayat.id == len(fayats):
                return 'стр. {0}/{0}'.format(len(fayats))
            elif self._ayat_id == ayat.id:
                return 'стр. {0}/{1}'.format(ayat_idx, len(fayats))
        raise BaseAppError('Page info not generated')


class NeighborAyats(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    def __init__(self, connection: Database, ayat_id: int):
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

    async def page(self) -> str:
        """Информация о странице.

        :return: str
        """
        ayats_count = await self._connection.fetch_val('SELECT COUNT(*) FROM ayats')
        actual_page_num = await self._connection.fetch_val(
            'SELECT COUNT(*) FROM ayats WHERE ayat_id <= :ayat_id',
            {'ayat_id': self._ayat_id},
        )
        return 'стр. {0}/{1}'.format(actual_page_num, ayats_count)


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

    async def page(self) -> str:
        """Информация о странице.

        :return: str
        """
        actual_page_num = 0
        rows = await self._connection.fetch_all(
            self._search_sql_query,
            {'search_query': '%{0}%'.format(await self._query.read())},
        )
        for idx, row in enumerate(rows, start=1):
            ayat = parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437
            if ayat.id == self._ayat_id:
                actual_page_num = idx
        return 'стр. {0}/{1}'.format(actual_page_num, len(rows))
