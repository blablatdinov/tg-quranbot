from aiogram.dispatcher import FSMContext

from app_types.intable import Intable
from exceptions import AyatNotFoundError
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.ayats.ayat_search import AyatSearchInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate


class AyatSearchByText(AyatSearchInterface):
    """Поиск аята по тексту."""

    _ayat_repository: AyatRepositoryInterface
    _query: str
    _state: FSMContext

    def __init__(
        self,
        ayat_repository: AyatRepositoryInterface,
        query: str,
        state: FSMContext,
    ):
        self._ayat_repository = ayat_repository
        self._query = query
        self._state = state
        self._ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.ayat_text_search_template

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises AyatNotFoundError: if ayat not found
        :returns: Ayat
        """
        ayats = await self._ayat_repository.search_by_text(self._query)
        if not ayats:
            raise AyatNotFoundError
        await self._state.update_data(search_query=self._query)
        return ayats[0]


class AyatSearchByTextAndId(AyatSearchInterface):
    """Поиск аята по тексту и идентификатору.

    Для пагинации в результатах поиска
    """

    _ayat_repository: AyatRepositoryInterface
    _state: FSMContext
    _ayat_id: Intable

    def __init__(
        self,
        ayat_repository: AyatRepositoryInterface,
        query: str,
        ayat_id: Intable,
    ):
        self._ayat_repository = ayat_repository
        self._query = query
        self._ayat_id = ayat_id
        self._ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.ayat_text_search_template

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises AyatNotFoundError: if ayat not found
        :returns: Ayat
        """
        ayats = await self._ayat_repository.search_by_text(self._query)
        if not ayats:
            raise AyatNotFoundError
        for ayat in ayats:
            if ayat.id == int(self._ayat_id):
                return ayat

        raise AyatNotFoundError


class AyatSearchByTextWithNeighbors(AyatSearchInterface):
    """Поиск аятов по номеру суры и аята с соседними аятами."""

    _ayat_search: AyatSearchInterface
    _neighbor_ayats_repository: NeighborAyatsRepositoryInterface

    def __init__(
        self,
        ayat_by_sura_num: AyatSearchInterface,
        neighbor_ayats_repository: NeighborAyatsRepositoryInterface,
    ):
        self._ayat_search = ayat_by_sura_num
        self._neighbor_ayats_repository = neighbor_ayats_repository

    async def search(self) -> Ayat:
        """Поиск.

        :returns: Ayat
        """
        ayat = await self._ayat_search.search()
        neighbors = await self._neighbor_ayats_repository.get_ayat_neighbors(ayat.id)
        if len(neighbors) == 2 and neighbors[0].id == ayat.id:
            ayat.right_neighbor = neighbors[1]
            return ayat
        elif len(neighbors) == 2 and neighbors[0].id != ayat.id:
            ayat.left_neighbor = neighbors[0]
            return ayat
        ayat.left_neighbor = neighbors[0]
        ayat.right_neighbor = neighbors[2]
        return ayat
