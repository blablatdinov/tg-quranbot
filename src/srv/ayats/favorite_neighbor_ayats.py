from typing import final, override

import attrs
from pyeo import elegant

from app_types.listable import AsyncListable
from exceptions.base_exception import BaseAppError
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.neighbor_ayats import NeighborAyats


@final
@attrs.define(frozen=True)
@elegant
class FavoriteNeighborAyats(NeighborAyats):
    """Класс для работы с соседними аятами в хранилище."""

    _ayat_id: int
    _favorite_ayats: AsyncListable[Ayat]

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят.

        :return: Ayat
        :raises AyatNotFoundError: if ayat not found
        """
        fayats = await self._favorite_ayats.to_list()
        for ayat_index, ayat in enumerate(fayats):
            ayat_id = await ayat.identifier().ayat_id()
            if ayat_id == self._ayat_id and ayat_index == 0:
                raise AyatNotFoundError
            elif ayat_id == self._ayat_id:
                return fayats[ayat_index - 1]
        raise AyatNotFoundError

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        fayats = await self._favorite_ayats.to_list()
        for ayat_index, ayat in enumerate(fayats):
            ayat_id = await ayat.identifier().ayat_id()
            if ayat_id == self._ayat_id and ayat_index + 1 == len(fayats):
                raise AyatNotFoundError
            elif ayat_id == self._ayat_id:
                return fayats[ayat_index + 1]
        raise AyatNotFoundError

    @override
    async def page(self) -> str:
        """Информация о странице.

        :return: str
        :raises BaseAppError: if page not generated
        """
        fayats = await self._favorite_ayats.to_list()
        for ayat_idx, ayat in enumerate(fayats, start=1):
            if self._ayat_id == 1:
                return 'стр. 1/{0}'.format(len(fayats))
            elif await ayat.identifier().ayat_id() == len(fayats):
                return 'стр. {0}/{0}'.format(len(fayats))
            elif self._ayat_id == await ayat.identifier().ayat_id():
                return 'стр. {0}/{1}'.format(ayat_idx, len(fayats))
        msg = 'Page info not generated'
        raise BaseAppError(msg)
